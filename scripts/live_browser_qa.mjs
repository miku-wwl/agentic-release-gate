// Independent, real-Chrome acceptance. Start releasegate.live before invoking.
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const origin = process.env.RELEASEGATE_QA_ORIGIN || 'http://127.0.0.1:8776';
assert.match(origin, /^http:\/\/127\.0\.0\.1:\d{4,5}$/);
const out = path.resolve(process.env.RELEASEGATE_QA_OUTPUT || '.artifacts/live-browser-qa');
await mkdir(out, {recursive:true});
const modulePath = process.env.RELEASEGATE_PLAYWRIGHT_MODULE;
const {chromium} = await import(modulePath ? pathToFileURL(path.resolve(modulePath)).href : 'playwright');
const browser = await chromium.launch({headless:true, channel:process.env.RELEASEGATE_CHROME ? undefined : 'chrome', executablePath:process.env.RELEASEGATE_CHROME || undefined});
const report = {started_at:new Date().toISOString(), origin, browser:browser.version(), method:'Independent headless Chrome; no ChatGPT UI automation, mocks or video', viewports:[], runs:[], expected_errors:[], unexpected_errors:[]};
const pause = ms => new Promise(resolve => setTimeout(resolve,ms));
async function api(route, body) {
  const response = await fetch(origin + route, body === undefined ? {} : {method:'POST', headers:{Origin:origin,'Content-Type':'application/json','X-ReleaseGate-Request':'live-console'},body:JSON.stringify(body)});
  const value = await response.json();
  assert.equal(response.ok,true,JSON.stringify(value));
  return value;
}
async function done(id) {
  for (let count=0; count<600; count++) {
    const value=await api(`/api/runs/${id}`);
    if(value.status !== 'running') return value;
    await pause(200);
  }
  throw new Error('Real backend job exceeded browser acceptance deadline');
}
async function geometry(page,label) {
  const value=await page.evaluate(() => ({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,deviceScale:devicePixelRatio,
    clipped:[...document.querySelectorAll('button, h1, h2, nav a, .live-repository, .live-topbar')].filter(el => {
      const r=el.getBoundingClientRect();return r.width && (r.left < -1 || r.right > innerWidth+1);
    }).map(el=>({text:el.textContent.trim(),left:el.getBoundingClientRect().left,right:el.getBoundingClientRect().right})),
    fonts:Object.fromEntries(['.live-sidebar nav a','#run-status','.source-note','.live-service'].map(selector=>[selector,getComputedStyle(document.querySelector(selector)).fontSize]))}));
  assert.equal(value.scrollWidth,value.width,`${label}: horizontal overflow`);
  assert.deepEqual(value.clipped,[],`${label}: clipped product controls or headings`);
  return {label,...value};
}
async function screenshot(page,name,fullPage=false) {
  await page.screenshot({path:path.join(out,`${name}.png`),fullPage,animations:'disabled'});
}
async function runByClick(page,button,expected,label,captureRunning=false) {
  const responsePromise=page.waitForResponse(response => response.url()===origin+'/api/runs' && response.request().method()==='POST');
  await button.click();
  const response=await responsePromise;
  assert.equal(response.status(),202);
  const {run_id}=await response.json();
  await page.waitForFunction(id => document.querySelector('#run-id').textContent === id,run_id);
  if(captureRunning) {
    await page.waitForSelector('[data-stage="tests"].current');
    assert.equal(await page.locator('#run-fresh').isDisabled(),true);
    await page.locator('#progress-title').scrollIntoViewIfNeeded();
    await screenshot(page,`${label}-running`);
  }
  const run=await done(run_id);
  await page.waitForFunction(id => document.querySelector('#run-id').textContent === id && ['Completed','Failed','Cancelled'].includes(document.querySelector('#run-status').textContent),run_id);
  assert.equal(run.status,'completed',JSON.stringify(run));
  assert.equal(run.result.decision.decision,expected);
  assert.equal(run.result.decision.execution_authorized,false);
  assert.equal(run.guard_verified,true);
  assert.equal(await page.locator('#decision-value').textContent(),expected);
  assert.equal(await page.locator('#test-count').textContent(),`${run.result.tests.passed} / ${run.result.tests.total}`);
  assert.equal(await page.locator('#verified-sha').textContent(),run.source_sha);
  assert.deepEqual(run.events.map(event=>event.stage),['preparing','tests','security','collecting','policy','report','completed']);
  assert.equal(run.processes.length,4);
  assert.ok(run.processes.slice(0,2).every(process=>process.inner_check_pid && process.pid));
  assert.equal(await page.locator('#empty-state').isVisible(),false);
  if(expected==='DENY') {
    assert.ok(run.result.decision.reasons.includes('SECURITY_HIGH'));
    assert.ok(await page.locator('#findings-body .HIGH').count()>0);
    assert.match(await page.locator('#scenario-label').textContent(),/Controlled scan-only/);
  } else assert.match(await page.locator('#next-gate').textContent(),/Human Approval Required/);
  await page.locator('#decision').scrollIntoViewIfNeeded();
  await screenshot(page,`${label}-decision`);
  await page.locator('#artifact-choice').selectOption('test-stdout');
  await page.getByRole('button',{name:'Inspect evidence',exact:true}).click();
  await page.waitForFunction(() => document.querySelector('#artifact-text').textContent.includes('passed'));
  assert.match(await page.locator('#artifact-hash').textContent(),/Original SHA256: [a-f0-9]{64}/);
  const geometryResult=await geometry(page,label);
  await screenshot(page,`${label}-full`,true);
  await writeFile(path.join(out,`${label}-run.json`),JSON.stringify(run,null,2)+'\n');
  report.runs.push({label,run_id,operation:run.operation,source_sha:run.source_sha,decision:expected,started_at:run.started_at,finished_at:run.finished_at,duration_seconds:run.duration_seconds,geometry:geometryResult});
  return run;
}
try {
  const viewports=[{width:1920,height:1080},{width:390,height:844},{width:320,height:800}];
  for (const viewport of viewports) {
    const context=await browser.newContext({viewport,deviceScaleFactor:1,reducedMotion:'reduce'});
    const page=await context.newPage();
    let expected409=false;
    page.on('pageerror',error=>report.unexpected_errors.push({viewport,error:error.message}));
    page.on('console',message=>{
      if(['error','warning'].includes(message.type())) {
        const record={viewport,type:message.type(),text:message.text()};
        if(expected409 && message.text().includes('409')) report.expected_errors.push(record);
        else report.unexpected_errors.push(record);
      }
    });
    const traces=[];
    page.on('response',async response=>{
      if(response.url().startsWith(origin+'/api/')) {
        try { traces.push({at:new Date().toISOString(),url:response.url(),status:response.status(),body:await response.json()}); } catch { /* Navigation can close a pending response. */ }
      }
    });
    await page.goto(origin+'/');
    await page.waitForFunction(()=>document.querySelector('#service-status').textContent==='Ready');
    assert.match(await page.locator('#empty-state').textContent(),/No verification has been run in this session\./);
    assert.equal(await page.locator('#decision-value').textContent(),'Awaiting verification');
    const body=await page.locator('body').innerText();
    assert.doesNotMatch(body,/Phase\s+[1-5]|production.ready|acceptance dashboard/i);
    const initial=await geometry(page,`${viewport.width}-initial`);
    await screenshot(page,`${viewport.width}-initial`);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Skip to content');
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(()=>document.activeElement.id),'live-main');
    await page.getByRole('link',{name:'Decision',exact:true}).click();
    assert.equal(new URL(page.url()).hash,'#decision');
    await page.getByRole('link',{name:'Verify',exact:true}).click();
    const first=await runByClick(page,page.locator('#run-fresh'),'ALLOW',`${viewport.width}-allow-a`,viewport.width===1920);
    if(viewport.width===1920) {
      const second=await runByClick(page,page.getByRole('button',{name:'Run ALLOW Verification',exact:true}),'ALLOW','1920-allow-b');
      assert.notEqual(first.run_id,second.run_id);
      assert.ok(first.finished_at<second.started_at);
    }
    await runByClick(page,page.getByRole('button',{name:'Run Security Rejection',exact:true}),'DENY',`${viewport.width}-deny`);
    await page.getByText('Safety boundary active · Technical status',{exact:true}).click();
    const technical=await page.locator('#technical-status').innerText();
    assert.match(technical,/DISABLED/);assert.match(technical,/REQUIRED \/ UNEXECUTED/);assert.match(technical,/execution_authorized=false/);
    if(viewport.width===1920) {
      // A real second caller occupies the server. The old page discovers a genuine 409.
      const competing=await api('/api/runs',{operation:'allow'});
      expected409=true;
      await page.locator('#run-fresh').click();
      await page.waitForFunction(()=>document.querySelector('#request-error').textContent.includes('Another verification is active'));
      await page.locator('#request-error').scrollIntoViewIfNeeded();
      await screenshot(page,'1920-concurrency-error');
      await api(`/api/runs/${competing.run_id}/cancel`,{});
      assert.equal((await done(competing.run_id)).status,'cancelled');
      expected409=false;
      // UI cancellation acts on another real process tree; there is no synthetic failure.
      const responsePromise=page.waitForResponse(response=>response.url()===origin+'/api/runs' && response.status()===202);
      await page.locator('#run-fresh').click();
      const {run_id}=await (await responsePromise).json();
      await page.waitForSelector('[data-stage="tests"].current');
      await page.getByRole('button',{name:'Cancel verification',exact:true}).click();
      assert.equal((await done(run_id)).status,'cancelled');
      await page.waitForFunction(()=>document.querySelector('#run-status').textContent==='Cancelled');
      assert.match(await page.locator('#run-error').textContent(),/cancelled/i);
      await screenshot(page,'1920-cancelled');
      report.cancellation_run_id=run_id;
      report.concurrency_run_id=competing.run_id;
    }
    report.viewports.push({viewport,initial,keyboard:'PASS',navigation:'PASS',functional:'PASS'});
    await writeFile(path.join(out,`${viewport.width}-api-trace.json`),JSON.stringify(traces,null,2)+'\n');
    await context.close();
  }
  assert.deepEqual(report.unexpected_errors,[]);
  report.status='PASS';
} catch(error) {
  report.status='FAIL';report.error=error.stack;process.exitCode=1;
} finally {
  report.finished_at=new Date().toISOString();
  await writeFile(path.join(out,'browser-qa.json'),JSON.stringify(report,null,2)+'\n');
  await browser.close();
  console.log(JSON.stringify({status:report.status,completed_runs:report.runs.length,output:out,error:report.error||null}));
}

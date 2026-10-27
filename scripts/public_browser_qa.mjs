import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const modulePath = process.env.RELEASEGATE_PLAYWRIGHT_MODULE || path.resolve(".artifacts/browser-tools/node_modules/playwright/index.mjs");
const { chromium } = await import(pathToFileURL(modulePath).href);
const base = (process.env.RELEASEGATE_BASE_URL || "http://127.0.0.1:8778").replace(/\/$/, "");
const output = path.resolve(process.env.RELEASEGATE_QA_OUTPUT || ".artifacts/public-live/browser-local");
const fresh = process.env.RELEASEGATE_QA_FRESH !== "0";
const chrome = process.env.RELEASEGATE_CHROME || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
await mkdir(output, { recursive: true });
const browser = await chromium.launch({headless: true, executablePath: chrome});
const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
const errors = [];
const assertions = [];
page.on("pageerror", (error) => errors.push(error.message));
const routes = ["/", "/decision-explorer.html", "/evidence-chain.html", "/research.html", "/audit-trail.html"];
const runs = [];

async function ready() {
  await page.locator("#public-mode").filter({hasText: /LIVE VERIFICATION|VERIFICATION PREVIEW/}).waitFor({timeout: 90000});
}
async function validate(run) {
  assert.equal(run.status, "COMPLETED");
  assert.equal(run.execution_authorized, false);
  assert.equal(run.production_execution, "DISABLED");
  assert.equal(run.test_summary.passed, 139);
  assert.equal(run.mandatory_present, 139);
  assert.equal(run.human_gate_executed, false);
  assert.ok(run.completed_at > run.started_at);
  const reply = await page.request.get(base + run.evidence);
  assert.equal(reply.status(), 200);
  const evidence = await reply.json();
  assert.equal(evidence.evidence_digest, run.evidence_digest);
  assert.equal(evidence.scan_only_fixture_executed, false);
  assert.equal(evidence.network_isolation, "LINUX_SECCOMP_NETWORK_DENIED");
  await writeFile(path.join(output, `${run.scenario}.json`), JSON.stringify({run, evidence}, null, 2));
}

try {
  await page.goto(base + "/", {waitUntil: "networkidle", timeout: 90000});
  await ready();
  const meta = await (await page.request.get(base + "/api/demo/scenarios")).json();
  if (fresh) {
    for (const scenario of ["POSITIVE_CANDIDATE", "SECURITY_HIGH"]) {
      await page.locator(`[data-scenario="${scenario}"]`).click();
      await page.waitForFunction(() => !document.getElementById("run-verification").disabled, null, {timeout: 65000});
      const accepted = page.waitForResponse((response) => response.url() === base + "/api/demo/verifications" && response.request().method() === "POST");
      await page.locator("#run-verification").click();
      const response = await accepted;
      assert.equal(response.status(), 202);
      const started = await response.json();
      await page.waitForFunction(() => document.getElementById("live-status").textContent === "RUNNING", null, {timeout: 5000});
      assertions.push(`${scenario}: actual RUNNING rendered`);
      await page.waitForFunction(() => ["COMPLETE", "ERROR"].includes(document.getElementById("live-status").textContent), null, {timeout: 75000});
      const run = await (await page.request.get(base + "/api/demo/verifications/" + started.run_id)).json();
      await validate(run);
      runs.push(run);
      assert.equal(run.policy_decision, scenario === "POSITIVE_CANDIDATE" ? "ALLOW" : "DENY");
      if (scenario === "SECURITY_HIGH") assert.ok(run.denial_reasons.includes("SECURITY_HIGH"));
      else assert.equal(run.next_gate, "HUMAN_APPROVAL");
      await page.screenshot({path: path.join(output, scenario === "POSITIVE_CANDIDATE" ? "desktop-allow.png" : "desktop-deny.png"), fullPage: true});
      await page.locator("#inspect-evidence").click();
      await page.locator("#live-evidence").waitFor({state: "visible"});
      assert.match(await page.locator("#live-evidence").textContent(), /LINUX_SECCOMP_NETWORK_DENIED/);
    }
    assert.notEqual(runs[0].run_id, runs[1].run_id);
    assert.ok(runs[0].started_at < runs[1].started_at);
  } else {
    const run = meta.history.find((item) => item.scenario === "SECURITY_HIGH" && item.status === "COMPLETED");
    assert.ok(run, "An actual completed negative run must exist for cached inspection");
    await page.goto(base + "/audit-trail.html", {waitUntil: "networkidle"});
    await ready();
    await page.locator("#live-history article").filter({hasText: run.run_id}).getByRole("button").click();
    await validate(run);
    runs.push(run);
  }
  for (const viewport of [{width:1920,height:1080}, {width:390,height:844}, {width:320,height:800}]) {
    await page.setViewportSize(viewport);
    for (const route of routes) {
      const response = await page.goto(base + route, {waitUntil: "networkidle"});
      assert.equal(response.status(), 200);
      await ready();
      const geometry = await page.evaluate(() => ({width: innerWidth, scroll: document.documentElement.scrollWidth, h1: document.querySelectorAll("h1").length}));
      assert.ok(geometry.scroll <= geometry.width, `${viewport.width} ${route}: ${JSON.stringify(geometry)}`);
      assert.equal(geometry.h1, 1);
      assertions.push(`${viewport.width}x${viewport.height} ${route}: no overflow, assets and API loaded`);
      if (route === "/audit-trail.html") {
        const history = await page.locator("#live-history").textContent();
        assert.ok(history.includes(runs.at(-1).run_id));
      }
    }
    await page.goto(base + "/decision-explorer.html", {waitUntil: "networkidle"});
    await ready();
    await page.locator('[data-scenario="SECURITY_HIGH"]').click();
    await page.locator("#view-cached").click();
    assert.equal(await page.locator("#live-decision").textContent(), "DENY");
    assert.match(await page.locator("#result-origin").textContent(), /CACHED COMPLETED RESULT/);
    await page.screenshot({path: path.join(output, `${viewport.width}-cached-deny.png`), fullPage:true});
    if (viewport.width < 400) {
      const menu = page.locator(".menu-button");
      await menu.click(); assert.equal(await menu.getAttribute("aria-expanded"), "true");
      await page.keyboard.press("Escape"); assert.equal(await menu.getAttribute("aria-expanded"), "false");
    }
  }
  assert.deepEqual(errors, []);
  await writeFile(path.join(output, "browser-acceptance.json"), JSON.stringify({status:"PASS",base,mode:fresh?"FRESH_RUNS":"CACHED_INSPECTION",run_ids:runs.map((run)=>run.run_id),assertions,errors},null,2));
  console.log(JSON.stringify({status:"PASS",base,run_ids:runs.map((run)=>run.run_id),viewports:3,pages:5,screenshots:output}));
} finally { await browser.close(); }

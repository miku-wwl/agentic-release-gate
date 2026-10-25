// Synthetic presentation unit cases; real execution is separately browser-tested.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const javascript = fs.readFileSync(path.join(root, 'src/releasegate/live_assets/live.js'), 'utf8');

class Element {
  constructor() { this.textContent = ''; this.value = ''; this.children = []; this.events = {}; this.dataset = {}; this.classList = {toggle(){}}; }
  addEventListener(name, fn) { this.events[name] = fn; }
  replaceChildren(...children) { this.children = children; }
  append(child) { this.children.push(child); }
}
async function render(result) {
  const elements = new Map();
  const element = id => { if(!elements.has(id)) elements.set(id,new Element()); return elements.get(id); };
  const button = new Element(); button.dataset.operation = 'allow';
  const document = {getElementById:element,createElement:()=>new Element(),querySelectorAll:selector=>selector==='[data-operation]'?[button]:[]};
  const run = {run_id:'unit-case',status:'completed',stage:'completed',events:[],processes:[],artifacts:[],operation:'allow',result};
  const context = vm.createContext({document,fetch:async route=>({ok:true,json:async()=>route==='/api/session'?{source_sha:'unit-source'}:route==='/api/runs'?{run_id:run.run_id}:run}),encodeURIComponent,window:{setTimeout}});
  vm.runInContext(javascript,context);
  await new Promise(resolve=>setImmediate(resolve));
  await button.events.click();
  return id=>element(id).textContent;
}
function result(decision,reasons,levels=[]) {
  return {decision:{decision,reasons,next_gate:decision==='ALLOW'?'HUMAN_APPROVAL':'BLOCKED',execution_authorized:false},security:{scanned_files:8,findings:levels.map(severity=>({severity,id:'unit',file:'unit.py',line:1}))}};
}
test('ALLOW is eligible and still requires unexecuted human approval',async()=>{
  const text=await render(result('ALLOW',['CHECKS_PASSED']));
  assert.equal(text('decision-gate-label'),'Eligible — Human Approval Required');
  assert.match(text('next-gate'),/Human Approval Required · Unexecuted/);
  assert.equal(text('chain-human'),'Required · Unexecuted');
});
test('security DENY blocks release without an ordinary approval escape',async()=>{
  const text=await render(result('DENY',['SECURITY_HIGH'],['HIGH']));
  assert.equal(text('decision-gate-label'),'Release Blocked — Security Policy Rejected');
  assert.doesNotMatch(text('decision-gate-label'),/Human Approval Required/);
  assert.match(text('next-gate'),/cannot override/);
  assert.equal(text('chain-human'),'Blocked · Unexecuted');
});
test('non-security DENY does not falsely claim a security rejection',async()=>{
  const text=await render(result('DENY',['TESTS_FAILED']));
  assert.equal(text('decision-gate-label'),'Release Blocked — Policy Rejected');
});
for(const [levels,expected] of [[[],'0 HIGH · 0 CRITICAL'],[['LOW','MEDIUM'],'0 HIGH · 0 CRITICAL'],[['HIGH'],'1 HIGH · 0 CRITICAL'],[['CRITICAL'],'0 HIGH · 1 CRITICAL'],[['HIGH','HIGH','CRITICAL'],'2 HIGH · 1 CRITICAL']]) {
  test(`severity values remain separate: ${expected}; ${levels.join(',')}`,async()=>{
    const text=await render(result('DENY',['SECURITY_HIGH'],levels));
    assert.equal(text('security-count'),expected);
  });
}
test('without a decision or evidence, no eligibility or zero-findings result is invented',async()=>{
  const text=await render(null);
  assert.equal(text('decision-gate-label'),'Verification required');
  assert.equal(text('chain-human'),'Unexecuted');
  assert.equal(text('security-count'),'—');
});

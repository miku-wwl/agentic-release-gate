"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const terminal = new Set(["completed", "failed", "cancelled"]);
  const controls = [...document.querySelectorAll("[data-operation]")];
  let currentRun = null;
  let currentStatus = null;
  let polling = false;
  const artifactNames = {"test-stdout":"Pytest stdout", "test-stderr":"Pytest stderr", "security-stdout":"Bandit stdout", "security-stderr":"Bandit stderr", junit:"JUnit report", bandit:"Bandit JSON", decision:"Policy decision JSON", tests:"Test evidence envelope", security:"Security evidence envelope", "review-json":"Review JSON", "review-md":"Review Markdown", "review-html":"Review HTML source", processes:"Process execution records", "source-manifest":"Source snapshot manifest", "execution-guard":"Scan-only execution guard records"};
  const text = (id, value) => { byId(id).textContent = value ?? "—"; };
  const busy = value => { controls.forEach(button => { button.disabled = value; }); byId("cancel-run").hidden = !value; };
  async function api(path, body) {
    const response = await fetch(path, body === undefined ? {cache:"no-store"} : {method:"POST", headers:{"Content-Type":"application/json", "X-ReleaseGate-Request":"live-console"}, body:JSON.stringify(body), cache:"no-store"});
    const value = await response.json();
    if (!response.ok) throw new Error(value.error || `Local service returned ${response.status}`);
    return value;
  }
  function requestError(error) { text("request-error", error.message || "Local service is unavailable. Start the service and retry."); byId("request-error").hidden = false; }
  function render(run) {
    currentRun = run.run_id;
    currentStatus = run.status;
    busy(!terminal.has(run.status));
    byId("empty-state").hidden = true;
    byId("run-meta").hidden = false;
    text("run-id", run.run_id);
    text("started-at", run.started_at);
    text("finished-at", run.finished_at || "In progress");
    text("duration", `${run.duration_seconds ?? 0} seconds`);
    text("run-status", run.status === "running" ? "In progress" : run.status === "completed" ? "Completed" : run.status === "cancelled" ? "Cancelled" : "Failed");
    text("live-announcement", `Verification ${run.stage}`);
    const completed = new Set(run.events.map(event => event.stage));
    document.querySelectorAll("[data-stage]").forEach(step => {
      step.classList.toggle("current", run.stage === step.dataset.stage && run.status === "running");
      step.classList.toggle("done", completed.has(step.dataset.stage) && run.stage !== step.dataset.stage);
    });
    text("run-error", run.error);
    byId("run-error").hidden = !run.error;
    byId("process-body").replaceChildren();
    for (const process of run.processes) {
      const row = document.createElement("tr");
      for (const value of [process.step, process.inner_check_pid || process.python_pid || process.pid || "Starting", process.exit_code ?? (process.finished_at ? "Unavailable" : "Running"), process.duration_seconds === undefined ? "In progress" : `${process.duration_seconds}s`]) { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); }
      byId("process-body").append(row);
    }
    text("verified-sha", run.source_sha);
    if (run.source_sha) text("repository-sha", run.source_sha);
    text("artifact-directory", `.artifacts/live-verification/${run.run_id}`);
    text("chain-commit", run.source_sha ? `${run.source_sha.slice(0,12)} · isolated source` : "Preparing source");
    text("scenario-label", run.operation === "security_rejection" ? "Controlled scan-only scenario" : "Committed source verification");
    const result = run.result;
    const decision = result?.decision;
    const tests = result?.tests;
    const security = result?.security;
    text("decision-value", decision?.decision || (run.status === "running" ? "Verification in progress" : "Decision unavailable"));
    const panel = byId("decision-panel");
    panel.classList.toggle("allow", decision?.decision === "ALLOW");
    panel.classList.toggle("deny", decision?.decision === "DENY");
    text("decision-summary", decision ? "Calculated by the existing release policy from this run's evidence." : "A decision requires actual checks and validated evidence.");
    byId("decision-reasons").replaceChildren();
    for (const reason of decision?.reasons || []) { const item = document.createElement("li"); item.textContent = reason; byId("decision-reasons").append(item); }
    text("next-gate", decision?.next_gate === "HUMAN_APPROVAL" ? "Next Gate: Human Approval Required · Unexecuted" : "Verification does not grant execution authorization.");
    text("evidence-digest", decision?.evidence_digest);
    text("test-count", tests ? `${tests.passed} / ${tests.total}` : "—");
    text("test-detail", tests ? `${tests.failed} failed · ${tests.errors} errors · ${tests.skipped} skipped` : "Waiting for this run's test evidence.");
    text("chain-tests", tests ? `${tests.passed}/${tests.total} passed` : "Not collected yet");
    const severities = {LOW:0, MEDIUM:0, HIGH:0, CRITICAL:0};
    for (const finding of security?.findings || []) if (finding.severity in severities) severities[finding.severity] += 1;
    text("security-count", security ? `${severities.HIGH + severities.CRITICAL} high / critical` : "—");
    text("security-detail", security ? `${severities.LOW} low · ${severities.MEDIUM} medium · ${security.scanned_files} files scanned` : "Waiting for this run's security evidence.");
    text("chain-security", security ? `${security.findings.length} actual findings` : "Not collected yet");
    text("chain-policy", decision?.decision || "Not evaluated");
    text("scan-scope", security ? `${security.scanned_files} files scanned` : "No scan yet");
    byId("findings-body").replaceChildren();
    for (const finding of security?.findings || []) {
      const row = document.createElement("tr");
      for (const [index, value] of [finding.severity, finding.id, `${finding.file}:${finding.line}`].entries()) { const cell = document.createElement("td"); cell.textContent = value; if (index === 0 && ["LOW","MEDIUM","HIGH","CRITICAL"].includes(value)) cell.className = value; row.append(cell); }
      byId("findings-body").append(row);
    }
    if (!security || security.findings.length === 0) { const row = document.createElement("tr"); const cell = document.createElement("td"); cell.colSpan = 3; cell.textContent = security ? "The scan returned no findings." : "Security evidence has not been collected."; row.append(cell); byId("findings-body").append(row); }
    const previous = byId("artifact-choice").value;
    byId("artifact-choice").replaceChildren();
    const placeholder = document.createElement("option"); placeholder.value = ""; placeholder.textContent = run.artifacts.length ? "Choose a generated artifact" : "No generated artifacts yet"; byId("artifact-choice").append(placeholder);
    for (const artifact of run.artifacts) { const option = document.createElement("option"); option.value = artifact.key; option.textContent = `${artifactNames[artifact.key] || artifact.key} · ${artifact.bytes} bytes`; byId("artifact-choice").append(option); }
    byId("artifact-choice").value = previous;
    byId("artifact-choice").disabled = run.artifacts.length === 0;
    byId("inspect-artifact").disabled = !byId("artifact-choice").value;
  }
  async function watch(runId) {
    if (polling) return;
    polling = true;
    try {
      while (currentRun === runId) {
        const run = await api(`/api/runs/${encodeURIComponent(runId)}`);
        render(run);
        if (terminal.has(run.status)) break;
        // This timer schedules a status request; it never invents progress or results.
        await new Promise(resolve => window.setTimeout(resolve, 500));
      }
    } catch (error) { requestError(error); text("service-status", "Connection interrupted"); throw error; }
    finally { polling = false; }
  }
  async function start(operation) {
    byId("request-error").hidden = true;
    busy(true);
    try {
      const value = await api("/api/runs", {operation});
      currentRun = value.run_id;
      text("service-status", "Local verification active");
      byId("artifact-inspector").open = false;
      await watch(value.run_id);
      text("service-status", "Ready for another run");
    } catch (error) { requestError(error); text("service-status", "Request failed"); busy(Boolean(currentRun && !terminal.has(currentStatus))); }
  }
  controls.forEach(button => button.addEventListener("click", () => start(button.dataset.operation)));
  byId("cancel-run").addEventListener("click", async () => {
    try { await api(`/api/runs/${encodeURIComponent(currentRun)}/cancel`, {}); }
    catch (error) { requestError(error); }
  });
  byId("artifact-choice").addEventListener("change", () => { byId("inspect-artifact").disabled = !byId("artifact-choice").value; });
  byId("inspect-artifact").addEventListener("click", async () => {
    try {
      const key = byId("artifact-choice").value;
      const value = await api(`/api/runs/${encodeURIComponent(currentRun)}/artifacts/${encodeURIComponent(key)}`);
      text("artifact-name", artifactNames[key] || key);
      text("artifact-hash", `Original SHA256: ${value.original_sha256}`);
      text("artifact-redaction", value.sanitized ? "Sanitized browser view. Original bytes are preserved in the local artifact directory." : "Browser text view matches the original artifact bytes.");
      text("artifact-text", value.text);
      byId("artifact-inspector").open = true;
    } catch (error) { requestError(error); }
  });
  async function initialize() {
    try {
      const session = await api("/api/session");
      text("repository-sha", session.source_sha);
      text("service-status", "Ready");
      busy(false);
      if (session.active_run_id) { currentRun = session.active_run_id; await watch(currentRun); }
    } catch (error) { requestError(error); text("service-status", "Local service unavailable"); }
  }
  initialize();
})();

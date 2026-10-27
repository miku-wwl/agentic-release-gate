/* Actual public API results only. No approval or production execution controls. */
"use strict";
(() => {
  const byId = (id) => document.getElementById(id);
  const put = (id, text) => { const node = byId(id); if (node) node.textContent = String(text ?? "—"); };
  const terminal = (run) => ["COMPLETED", "FAILED", "TIMED_OUT"].includes(run.status);
  let selected = "POSITIVE_CANDIDATE";
  let metadata = null;
  let current = null;
  let polling = false;
  let cooldownTimer = null;

  async function request(path, options = {}) {
    const response = await fetch(path, {cache: "no-store", credentials: "omit", signal: AbortSignal.timeout(25000), ...options});
    const value = await response.json();
    if (!response.ok) {
      const error = new Error(value.error || `HTTP ${response.status}`);
      error.status = response.status;
      throw error;
    }
    return value;
  }

  function controls() {
    const running = current && !terminal(current);
    const unavailable = !metadata || !!metadata.active_run_id || metadata.cooldown_remaining > 0 || metadata.daily_starts_remaining < 1;
    if (byId("run-verification")) byId("run-verification").disabled = !!running || unavailable;
    document.querySelectorAll("[data-scenario]").forEach((button) => { button.disabled = !!running; });
    const cached = metadata?.history.find((run) => run.scenario === selected && terminal(run));
    if (byId("view-cached")) byId("view-cached").hidden = !cached || !!running;
  }

  function render(run, cached = false) {
    current = run;
    selected = run.scenario;
    document.querySelectorAll("[data-scenario]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.scenario === selected)));
    if (!byId("live-result")) return;
    byId("live-result").hidden = false;
    const finished = terminal(run);
    put("live-status", run.status === "COMPLETED" ? "COMPLETE" : finished ? "ERROR" : "RUNNING");
    put("result-origin", cached ? "CACHED COMPLETED RESULT · NO NEW EXECUTION" : "ACTUAL SERVER EXECUTION · FIXED DEMO SCENARIO");
    put("live-decision", finished ? run.policy_decision : run.stage);
    byId("live-decision").className = `live-decision ${finished && run.policy_decision === "ALLOW" ? "allow-text" : finished ? "deny-text" : "pending-text"}`;
    put("live-reasons", finished ? run.denial_reasons.join(" · ") : "Waiting for actual test, scanner and policy evidence.");
    put("live-next-gate", finished ? (run.next_gate || "NONE · resolve denial") : "Not yet evaluated");
    put("live-tests", run.test_summary ? `${run.test_summary.passed} / ${run.test_summary.total} passed` : "Executing…");
    put("live-security", run.security_summary ? run.security_summary.findings.filter((f) => ["HIGH", "CRITICAL"].includes(f.severity)).length : "Awaiting scan");
    put("live-duration", `${(run.duration_ms / 1000).toFixed(2)} s`);
    put("live-candidate", run.candidate_sha);
    put("live-scenario-id", run.scenario);
    put("live-run-id", run.run_id);
    put("live-time", run.started_at);
    put("live-digest", run.evidence_digest || "Pending verified evidence");
    put("live-notice", finished ? (run.status === "COMPLETED" ? "Actual verification completed. Inspect its evidence below." : "Verification failed closed. No release eligibility is granted.") : `Server status: ${run.stage}. This page polls actual backend state.`);
    const chain = byId("live-chain");
    chain.replaceChildren();
    [
      ["Candidate", run.candidate_sha.slice(0, 12)],
      ["Tests", run.test_summary ? `${run.test_summary.passed} passed · ${run.mandatory_present}/${run.mandatory_required} mandatory` : "Awaiting evidence"],
      ["Security scan", run.security_summary ? `${run.security_summary.scanned_files} files · ${run.security_summary.findings.length} findings` : "Awaiting evidence"],
      ["Policy", finished ? run.policy_decision : "Not complete"],
      ["Human approval", run.next_gate === "HUMAN_APPROVAL" ? "REQUIRED · UNEXECUTED" : "No approval bypass · UNEXECUTED"],
    ].forEach(([title, text]) => {
      const item = document.createElement("li");
      const strong = document.createElement("strong"); strong.textContent = title;
      const span = document.createElement("span"); span.textContent = text;
      item.append(strong, span); chain.append(item);
    });
    byId("inspect-evidence").disabled = !finished;
    controls();
  }

  function renderHistory() {
    const container = byId("live-history");
    if (!container) return;
    container.replaceChildren();
    if (!metadata.history.length) { container.textContent = "No runs in this instance. Start a fresh verification above."; return; }
    metadata.history.forEach((run) => {
      const article = document.createElement("article");
      const label = document.createElement("strong"); label.textContent = `${run.scenario} · ${run.status} · ${terminal(run) ? run.policy_decision : run.stage}`;
      const identity = document.createElement("code"); identity.textContent = run.run_id;
      const detail = document.createElement("span"); detail.textContent = `${run.started_at} · ${(run.duration_ms / 1000).toFixed(2)} s`;
      const button = document.createElement("button"); button.type = "button"; button.className = "text-link"; button.textContent = "Inspect this actual run →";
      button.addEventListener("click", () => { render(run, terminal(run)); byId("live-result").scrollIntoView({block: "start"}); });
      article.append(label, identity, detail, button); container.append(article);
    });
  }

  async function refresh() {
    metadata = await request("/api/demo/scenarios");
    put("public-mode", metadata.live_e2e_accepted ? "LIVE VERIFICATION" : "VERIFICATION PREVIEW");
    if (!current) {
      put("live-status", metadata.active_run_id ? "RUNNING" : "READY");
      put("live-notice", metadata.active_run_id ? "Another verification is active. Wait or inspect completed evidence." : `Ready · ${metadata.daily_starts_remaining} starts remaining this instance UTC day · ${metadata.limits.timeout_seconds} s run limit · ${metadata.limits.cooldown_seconds} s cooldown.`);
    }
    if (metadata.cooldown_remaining > 0) {
      put("live-notice", `Server cooldown: ${metadata.cooldown_remaining} s. Completed results remain inspectable.`);
      clearTimeout(cooldownTimer); cooldownTimer = setTimeout(() => refresh().catch(showError), 5000);
    }
    controls(); renderHistory();
    return metadata;
  }

  function showError(error) { put("live-status", "ERROR"); put("live-notice", error.message + ". Inspect history before retrying; a failed network response is not retried automatically."); }

  async function poll(runId) {
    if (polling) return;
    polling = true;
    try {
      for (;;) {
        const run = await request(`/api/demo/verifications/${runId}`);
        render(run);
        if (terminal(run)) break;
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      await refresh();
    } catch (error) { showError(error); }
    finally { polling = false; controls(); }
  }

  document.querySelectorAll("[data-scenario]").forEach((button) => {
    button.addEventListener("click", () => {
      selected = button.dataset.scenario;
      document.querySelectorAll("[data-scenario]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      current = null;
      byId("live-result").hidden = true;
      byId("live-evidence").hidden = true;
      put("live-status", "READY");
      put("live-notice", `${selected} selected. A fresh result requires actual server execution.`);
      controls();
    });
  });
  byId("run-verification")?.addEventListener("click", async () => {
    byId("run-verification").disabled = true;
    current = null;
    byId("live-result").hidden = true;
    put("live-status", "REQUESTING");
    put("live-notice", "Requesting a fresh verification. No result is assumed.");
    byId("live-evidence").hidden = true;
    try {
      const run = await request("/api/demo/verifications", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({scenario: selected})});
      sessionStorage.setItem("releasegate-public-run", run.run_id);
      render(run); await poll(run.run_id);
    } catch (error) { showError(error); await refresh().catch(() => {}); }
  });
  byId("view-cached")?.addEventListener("click", () => {
    const run = metadata.history.find((item) => item.scenario === selected && terminal(item));
    if (run) render(run, true);
  });
  byId("inspect-evidence")?.addEventListener("click", async () => {
    try {
      const evidence = await request(current.evidence);
      byId("live-evidence").textContent = JSON.stringify(evidence, null, 2);
      byId("live-evidence").hidden = false;
    } catch (error) { showError(error); }
  });
  byId("refresh-history")?.addEventListener("click", () => refresh().catch(showError));
  refresh().then(async () => {
    const id = sessionStorage.getItem("releasegate-public-run");
    const run = metadata.history.find((item) => item.run_id === id);
    if (run && byId("live-result")) {
      render(run, terminal(run));
      if (!terminal(run)) await poll(run.run_id);
    }
  }).catch(showError);
})();

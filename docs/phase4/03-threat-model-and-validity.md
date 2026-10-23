# Threat model and validity

Scope: release eligibility on a trusted Python host, with untrusted report bytes
and AI advice. Protected assets are candidate identity, completeness of mandatory
checks, security findings, policy reasons and the human execution boundary.

| Threat | Existing or Phase 4 control | Residual limit |
|---|---|---|
| Old or cross-pipeline artifact substituted | Expected SHA, equal current context, source and raw digests | Self-described metadata is not cryptographic runner attestation |
| Failed/skipped/omitted tests presented as success | Reviewed identity manifest, raw JUnit parsing, no skips | Trusted reviewers can still change tests/manifests |
| Missing/corrupt scan or reduced scope | Raw Bandit parsing, exact source scan scope, HIGH/CRITICAL denial | Bandit is a limited static scanner, not exhaustive vulnerability assessment |
| Forged favorable AI review | Advisory is separate from evaluate/ApprovalFacts; strict closed schema | Offline references cannot authenticate server state |
| Historical session relabelled as current | Curated session/revision/correction identity and explicit candidate comparison | New verified sessions require reviewed catalog changes |
| HTML/Markdown injection | Escaping, no scripts, static CSP, no external resources | Opening a report does not validate its publisher |
| Input traversal, symlink escape, huge reports | Resolve inputs inside workspace, fixed artifact names, 10 MiB reports/64 KiB advisory | Trusted filesystem; no malicious concurrent-host isolation or TOCTOU guarantee |
| Credential disclosure | No environment/log dumps; closed fields; common credential patterns rejected | Arbitrary secrets cannot be reliably inferred from all prose; operator review remains necessary |
| Advice impersonates approval/deployment | No approval input path; final production gate and release stay closed | No production identity/execution adapter exists |

## Internal validity

Actual pytest and Bandit collection is distinguished from policy-only approval
fixtures. Expected outcomes are fixed in source before measurement. A row is
correct only if its decision, required reason, exit and false execution boundary
match. Fresh output directories and raw digests prevent accidental stale artifacts.
Unit tests intentionally use synthetic objects; the scenario command supplies
separate real collection evidence. Retain raw artifacts for inspection.

The experiment and implementation share a codebase and author, so this is not an
independent security certification. Negative cases test specified faults, not
unknown attacks. Corruption/context cases mutate metadata deliberately; they are
not observations of a real compromised GitLab runner.

## External and construct validity

Three repetitions on a local Windows Python 3.12 environment characterize only
that environment. Genuine GitLab CI tests the Linux slim image separately. Neither
proves general production safety, multi-user identity, independent attestation,
deployment success or exactly-once effects. Gate ALLOW measures eligibility, not
release success. A final approval policy fixture measures binding validation, not
consent. Historical Duo execution proves the observed review only; no new model
quality, custom Flow execution, autonomous repair or final-SHA review is inferred.

Process and policy changes require review. Do not resolve ambiguous external
effects by retrying. No external release effects are possible in this milestone.

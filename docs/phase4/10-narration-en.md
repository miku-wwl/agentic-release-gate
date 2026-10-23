# Planned English narration

This is a production script, not recorded audio. Target runtime is 164 seconds;
measure the actual take and revise pacing before production. Stage cues and the
following title are not spoken. Pair with the storyboard and real evidence index.

## Spoken script

A green pipeline is useful. But it does not answer every release question.
Did the required tests actually run? Does the security report belong to this
candidate? And who has permission to take the next step?

ReleaseGate brings those questions into one reviewable decision.

Here is a genuine GitLab Duo Code Review session from October fourteenth.
It is historical evidence, and the report preserves the revision it reviewed.
We are not presenting it as a new agent run.

Duo identified a concrete integration problem. Our demonstration script asked
Git for the current commit, but the slim Python CI image did not include Git.
That meant a locally successful demo could fail on the real runner.

Duo recommended using the commit identity supplied by GitLab CI.
Codex implemented the subsequent correction. The recommendation and the code
change have separate attribution and source references.

The genuine GitLab pipeline then provides engineering evidence. The original
ninety-six mandatory tests remain required, alongside the new Phase Four tests.
Security scanning remains enforced, and the manual review boundary stays closed.

ReleaseGate checks more than a passing count. It validates the exact mandatory
test identities, rejects skipped tests, and checks the candidate commit, source
digest, execution context, and raw artifact integrity.

The human review report presents the outcome, the evidence, and what remains
unverified. This candidate is eligible for human review. ALLOW does not authorize
a deployment. The historical Duo advice remains visible with its original SHA.

Now consider real negative evidence. This isolated fixture produces a high-severity
Bandit finding. Another fixture contains an actually failing mandatory test.
Both result in DENY. A favorable AI recommendation cannot override either result.
The research suite records commands, exits, timings and provenance across repeated
trials, with its small local sample clearly disclosed.

Finally, the human boundary is explicit. Production requires trusted final approval
and separate execution authorization. This application has no release executor;
its release command denies the operation.

ReleaseGate demonstrates Assisted automation: useful AI advice, reproducible
engineering checks, deterministic eligibility, and a clear next step for the human
reviewer. Evidence becomes easier to inspect without becoming permission to act.

## Recording notes

Use the exact final test count in an on-screen label sourced from the qualified
job. Do not add a fabricated quantitative impact claim. Actual spoken duration,
audio quality and subjective listening remain NOT RUN until a separate recording.

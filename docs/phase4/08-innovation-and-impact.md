# Innovation and practical impact

Audience: release reviewers who need to decide whether a specific candidate has
sufficient engineering evidence to move to human approval.

| Signal | Meaning in ReleaseGate | What it does not establish |
|---|---|---|
| Ordinary CI passes | A particular job completed successfully | All required identities, matched evidence context or production authority |
| AI recommendation | A cited finding and proposed correction | A waived failure, human consent or source change performed by Duo |
| Commit-bound evidence | Candidate SHA plus source/context/raw integrity checks | Cryptographic runner attestation or an honest compromised host |
| Deterministic eligibility | Policy v2 checks all evidence and emits exact reasons | Release execution permission |
| Human execution authorization | A separately required future authenticated approval/authorization boundary | Something an ALLOW string or advisory can confer |

The contribution is a small, inspectable bridge between advisory AI, independently
collected engineering checks and a human release decision. The report makes both
positive evidence and missing proof legible. Historical review attribution avoids
giving a later candidate the credibility of an earlier review without disclosure.
Real failing tests, missing identities, inconsistent artifacts and high-severity
findings demonstrate why a positive summary alone is insufficient.

This addresses a concrete review ambiguity rather than claiming a new general
agent framework. Novelty is bounded to this product's composition and evidence
experience; no claim of unprecedented research is made. Local measured correctness
supports the specified scenarios only. There is no measured cost saving, defect
reduction, sustainability gain or deployment-speed improvement. User studies,
independent artifact attestation and deployment integration would be separate work.

# Shared Runtime feasibility — Phase 1.1

Checked independently on **2026-10-14**. This supersedes the v0.1.0 feasibility
assessment; the historical `phase1-handoff.md` remains intact.

## Decision

**License and pinned Python 3.13 installation: PASS. ReleaseGate execution integration:
NOT IMPLEMENTED.** Verify actual GitLab Duo/CI first. The current eligibility pipeline
does not need a Runtime executor, database or authorization composition.

## Release and license evidence

Live command:

```text
git ls-remote https://github.com/miku-wwl/agentic-intent-gate.git refs/tags/v0.2.0 'refs/tags/v0.2.0^{}'
b193d38a4804725d44ca536a3bd9778679cc7b4c  refs/tags/v0.2.0
7261fdd2f47d2b15fabe8faac527eeee37338eb1  refs/tags/v0.2.0^{}
```

The tag object type is `tag`; its peeled object is a commit. Read-only `git show`
against that exact commit confirmed `LICENSE` (MIT, copyright 2026 Weilai Wang),
`version = "0.2.0"`, `requires-python = ">=3.13,<3.14"`, `license = "MIT"` and
`license-files = ["LICENSE"]`. The installed metadata and packaged license agree.
MIT reuse is compatible with this MIT consumer; preserve the upstream copyright and
license notice when distributing its code/package. A private Git credential is not
part of the dependency URL. [Pinned license](https://github.com/miku-wwl/agentic-intent-gate/blob/7261fdd2f47d2b15fabe8faac527eeee37338eb1/LICENSE),
[package metadata](https://github.com/miku-wwl/agentic-intent-gate/blob/7261fdd2f47d2b15fabe8faac527eeee37338eb1/pyproject.toml).

The old release's missing-license finding is historical; it is not an unresolved
licensing blocker for **v0.2.0**. No shared core source was modified or copied into
the application.

## Reference-document discrepancy

The pinned `docs/V0.2.0-CONSUMER-HANDOFF.md`, `docs/ADAPTER_GUIDE.md` and
`examples/consumer/app.py` were read. The handoff/adapter describe v0.2.0, but
`docs/AGENTS-dependence.md` **inside the release tag still names v0.1.0**. A live
remote check confirmed the corrected guide at documentation commit
`65767556f6de78e3fb7c2e6141a3769d20c76a99`. Use that immutable guide reference;
the executable dependency remains pinned to `7261fdd...`, never moving `main`.
[Release handoff](https://github.com/miku-wwl/agentic-intent-gate/blob/v0.2.0/docs/V0.2.0-CONSUMER-HANDOFF.md),
[corrected dependency guide](https://github.com/miku-wwl/agentic-intent-gate/blob/65767556f6de78e3fb7c2e6141a3769d20c76a99/docs/AGENTS-dependence.md).

## Actual isolated installation

From this repository, using a fresh ignored environment:

```powershell
uv venv --python 3.13 .artifacts/phase1.1-20261014/runtime-py313
uv pip install --python .artifacts/phase1.1-20261014/runtime-py313/Scripts/python.exe `
  "agentic-intent-gate @ git+https://github.com/miku-wwl/agentic-intent-gate.git@7261fdd2f47d2b15fabe8faac527eeee37338eb1"
```

Results: CPython **3.13.9**, **0.2.0**, **23 installed packages**, dependency check
PASS. `python -I` imports from the environment's `Lib/site-packages`, not the adjacent
editable checkout. Installed `direct_url.json`:

```json
{"url":"https://github.com/miku-wwl/agentic-intent-gate","vcs_info":{"vcs":"git","commit_id":"7261fdd2f47d2b15fabe8faac527eeee37338eb1","requested_revision":"7261fdd2f47d2b15fabe8faac527eeee37338eb1"}}
```

There is no editable `dir_info`. All **57 RECORD file hashes** passed. Installed
`runtime.py` and the packaged license match the pinned Git text after LF/CRLF
normalization. The Windows-built module has 247 CRLF lines versus Git's LF, so this
is **not** a byte-identical Git-blob claim. Source commit and semantic text identity
are verified, and installed bytes match their RECORD hashes.

Evidence: `.artifacts/phase1.1-20261014/runtime-install-py313.txt`,
`runtime-api.json` and the ignored `runtime_api_probe.py` used with `python -I`.
No Runtime was opened, no capability provisioned, no Plan approved or Action dispatched.

## Public API — installed signatures

```text
ToolBinding(tool_name, tool_version, adapter_id, binding_revision, target, execution_scope)
ToolCapability(binding, description, input_schema, target_argument=None, semantic_rule=None)
ExecutableRegistry(executor=None, *, binding=None)
CapabilityVerifier(token=None, *, subject_id=None, binding=None, operations=())
BoundCapabilityAuthorization(verifier, *, policy_revision)
execution_budget_binding(binding, execution_timeout_seconds)
open_runtime(*, gate_path, provider, capability, registry, verifier, policy, predecessor_stopped=False, execution_timeout_seconds=5)
```

The full annotated signatures are in `runtime-api.json`. Public imports and pure
binding-helper probes passed: five seconds preserves the base binding; fifteen
produces `probe-v2.exec-15s`; nine invalid values are rejected. These probes do not
prove persistence, authorization or executor behavior in ReleaseGate.

The supported composition has one trusted single-step `SIDE_EFFECT` tool, strict
Plan/input identity, exact approval, independent authorization and durable Action/
receipt handling. Ambiguous outcomes stay Unknown without blind retry. No generic
multi-agent/multi-tool engine, production human authentication or universal remote
exactly-once guarantee is provided. [Adapter contract](https://github.com/miku-wwl/agentic-intent-gate/blob/v0.2.0/docs/ADAPTER_GUIDE.md).

The default adapter budget is five seconds; trusted opt-in is bounded at fifteen.
Extended profiles require fresh reviewed binding/scope/ledger and fresh approval/
authorization; old Actions must not gain authority. Deadlines only shorten the host
budget, and a fifteen-second profile needs a consumer request envelope beyond the
bundled ten-second HTTP deadline. These execution/recovery rules were inspected,
not independently exercised as ReleaseGate integration tests in this phase.
[Budget qualification](https://github.com/miku-wwl/agentic-intent-gate/blob/v0.2.0/docs/V0.2.0-CONSUMER-HANDOFF.md).

## Python compatibility and future dependency decision

An actual install attempt in a second fresh **3.12.13** environment returned exit 1:

```text
Because the current Python version (3.12.13) does not satisfy Python>=3.13,<3.14
... agentic-intent-gate==0.2.0 cannot be used.
```

It installed no packages; no `--ignore-requires-python` or metadata modification was
used. ReleaseGate already allows `>=3.12,<3.14`; `.python-version` and the existing
CI remain on 3.12. Dependencies and `uv.lock` are unchanged. See the Phase 1.1 handoff
for actual application validation on both interpreters.

The next competition milestone needs genuine Duo review and CI evidence, not an
execution Runtime. Defer adding the dependency until a trusted human identity,
authorization policy, concrete release executor and verified receipt contract are
in scope. At that point adopt/review a 3.13 composition and its lock explicitly,
reuse the exact Git pin, retain MIT notices, and run the full external-consumer
acceptance chain. The reference's scripted consent is never authenticated approval.

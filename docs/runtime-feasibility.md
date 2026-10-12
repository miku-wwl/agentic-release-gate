# Shared Runtime feasibility evidence

Checked on 2026-10-13 before product code changes. This is a compatibility report,
not a Runtime integration acceptance claim.

## Release identity — PASS

```text
git ls-remote https://github.com/miku-wwl/agentic-intent-gate.git refs/tags/v0.1.0 'refs/tags/v0.1.0^{}'
ce0a516baf857bf79b53237677fff7fd3c50de95  refs/tags/v0.1.0
fd742b783058a53400c465b4ab59c6e80715895a  refs/tags/v0.1.0^{}
```

## License compatibility — BLOCKED

The pinned checkout was examined with `git ls-tree -r --name-only <pin>` for
license/copying/notice paths and `git grep -i` over pinned README, pyproject and docs.
No licensing declaration was found. `git show <pin>:LICENSE` returned:

```text
fatal: path 'LICENSE' does not exist in 'fd742b783058a53400c465b4ab59c6e80715895a'
```

The current task explicitly requires independently verified license compatibility
before depending on the core. An MIT license on this consumer cannot license another
repository's code. No package installation, copying or integration was performed
for this app. The owner must establish compatible reuse rights for the pinned code;
then review the applicable license and notice obligations. Do not silently change
the pin or assume a later license applies retroactively.

## Python baseline — BLOCKED for 3.12

Actual pinned `pyproject.toml`:

```toml
name = "agentic-intent-gate"
version = "0.1.0"
requires-python = ">=3.13,<3.14"
```

ReleaseGate currently runs under 3.12.13. If this exact runtime is required, use a
3.13 consumer environment and update/test the baseline. No ignored Requires-Python
check or modified core is acceptable.

## API reconnaissance — PARTIAL, not pinned installation verification

The exact pinned `examples/consumer/app.py` was read using `git show`. An existing
installed editable distribution from the sibling core checkout was inspected with
`inspect.signature`, producing:

```text
VERSION=0.1.0
ToolBinding(tool_name: str, tool_version: str, adapter_id: str, binding_revision: str, target: str, execution_scope: str)
ToolCapability(binding, description: str, input_schema, target_argument: str | None = None, semantic_rule = None)
ExecutableRegistry(executor=None, *, binding=None)
BoundCapabilityAuthorization(verifier, *, policy_revision: str)
open_runtime(*, gate_path, provider, capability, registry, verifier, policy, predecessor_stopped=False)
```

Its `direct_url.json` was `file:///D:/workshop/oct/agentic-intent-gate` with editable
installation, and that checkout HEAD was
`35e0cf1b6de8b586d50b40a9e5e273332f3888e7`, **not** the release pin. The inspected
public integration files showed no diff from the pin, but this is insufficient to
qualify the complete installation. No working consumer was claimed from this probe.

## Deferred activation

After licensing and interpreter resolution, merge this exact dependency into the
existing configuration (do not replace other dependencies):

```text
agentic-intent-gate @ git+https://github.com/miku-wwl/agentic-intent-gate.git@fd742b783058a53400c465b4ab59c6e80715895a
```

Verify the installed distribution's Git `direct_url.json` commit, inspect actual
public signatures, and run the external-consumer acceptance suite. One trusted
release tool must bind exact version/target/adapter/scope. Persistent Run and exact
Plan approval, authorization, durable Action claiming, ambiguity handling and
receipts belong to the Runtime. ReleaseGate does not reimplement them.

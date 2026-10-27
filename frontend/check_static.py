"""Parse CSS syntax with pinned tinycss2; run in an isolated QA tool environment."""

import json
import sys
from pathlib import Path

import tinycss2

root = Path(__file__).resolve().parent
errors = []
sources = [Path(value) for value in sys.argv[1:]] or [root / "assets/console.css"]
counts = {"stylesheets": len(sources), "qualified_rules": 0, "at_rules": 0, "declarations": 0}


def inspect_rules(rules):
    for rule in rules:
        if rule.type == "error":
            errors.append(f"{rule.source_line}:{rule.source_column}: {rule.message}")
        elif rule.type == "at-rule":
            counts["at_rules"] += 1
            if rule.content is not None:
                inspect_rules(
                    tinycss2.parse_rule_list(rule.content, skip_comments=True, skip_whitespace=True)
                )
        elif rule.type == "qualified-rule":
            counts["qualified_rules"] += 1
            for declaration in tinycss2.parse_declaration_list(
                rule.content, skip_comments=True, skip_whitespace=True
            ):
                if declaration.type == "error":
                    errors.append(f"{declaration.source_line}: {declaration.message}")
                elif declaration.type == "declaration":
                    counts["declarations"] += 1


for source in sources:
    inspect_rules(
        tinycss2.parse_stylesheet(
            source.read_text(encoding="utf-8"), skip_comments=True, skip_whitespace=True
        )
    )
print(
    json.dumps(
        {
            "tool": "tinycss2",
            "version": tinycss2.__version__,
            "status": "FAIL" if errors else "PASS",
            "counts": counts,
            "errors": errors,
        }
    )
)
raise SystemExit(1 if errors else 0)

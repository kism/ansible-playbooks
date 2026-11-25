#!/usr/bin/env -S uv run python
"""Find tasks that always show up as drift in scripts/plan (--check --diff on a converged host).

- changed_when: true reports a change on every run, detect the real change instead (creates/removes,
  a version compare, a before/after hash). Fine behind a when:, inside a rescue: (only runs on failure)
  or with creates/removes, since then it only runs when something actually needs doing.
- state: latest reports every pending package update as drift. Keyrings are exempt, a stale keyring
  breaks signature checks on the next install, and nothing else updates archlinux-keyring.

maintenance_* roles aren't in the build playbooks, so they're skipped.

Usage: ./scripts/check_mode_audit.py
"""

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
LATEST_ALLOWED = {"archlinux-keyring"}


def tasks(node: object, gated: bool = False) -> list[tuple[dict, bool]]:
    """Every (task, gated) in a parsed tasks file. Gated means it only runs when something needs doing."""
    if isinstance(node, list):
        return [t for item in node for t in tasks(item, gated)]
    if isinstance(node, dict):
        gated = gated or "when" in node
        nested = [
            *tasks(node.get("block", []), gated),
            *tasks(node.get("rescue", []), True),
            *tasks(node.get("always", []), gated),
        ]
        return [(node, gated), *nested]
    return []


def module_args(task: dict) -> list[dict]:
    return [v for v in task.values() if isinstance(v, dict)]


def main() -> int:
    problems = 0
    for path in sorted((REPO / "roles").glob("*/tasks/**/*.yml")):
        if path.relative_to(REPO / "roles").parts[0].startswith("maintenance_"):
            continue
        for task, gated in tasks(yaml.safe_load(path.read_text()) or []):
            name = task.get("name", "(unnamed)")
            args = module_args(task)
            has_creates = any("creates" in a or "removes" in a for a in args)
            if task.get("changed_when") is True and not gated and not has_creates:
                print(f"{path.relative_to(REPO)}: {name}: changed_when: true")
                problems += 1
            latest = [
                a
                for a in args
                if a.get("state") == "latest" and a.get("name") not in LATEST_ALLOWED
            ]
            if not gated and latest:
                print(f"{path.relative_to(REPO)}: {name}: state: latest")
                problems += 1

    if not problems:
        print("All good, no tasks that always report changed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

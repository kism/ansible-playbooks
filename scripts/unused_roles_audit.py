#!/usr/bin/env -S uv run python
"""Find roles that no playbook uses.

UNUSED     not referenced by any playbook, or by any role a playbook uses
COMMENTED  only reachable through commented out lines (build playbook toggles, info only)

A role counts as used if its name appears in a playbook, or in the tasks/handlers/meta
of a role that's used (include_role, meta_onboard's loop list, meta dependencies).

Usage: ./scripts/unused_roles_audit.py
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROLES = sorted(p.name for p in (REPO / "roles").iterdir() if p.is_dir())
# \b treats _ as a word char, so configure_docker won't match configure_docker_arr
ROLE_RE = re.compile(r"\b(" + "|".join(sorted(ROLES, key=len, reverse=True)) + r")\b")


def mentions(paths: list[Path], *, include_comments: bool) -> set[str]:
    found = set()
    for path in paths:
        for line in path.read_text().splitlines():
            if not include_comments and line.lstrip().startswith("#"):
                continue
            found.update(ROLE_RE.findall(line))
    return found


def reachable(roots: set[str], refs: dict[str, set[str]]) -> set[str]:
    seen, todo = set(), list(roots)
    while todo:
        role = todo.pop()
        if role not in seen:
            seen.add(role)
            todo.extend(refs[role])
    return seen


def main() -> int:
    playbooks = [p for p in REPO.glob("*.yml") if not p.name.endswith(".tmp.yml")]
    role_files = {
        r: [p for d in ("tasks", "handlers", "meta") for p in (REPO / "roles" / r / d).rglob("*.yml")] for r in ROLES
    }

    active = reachable(
        mentions(playbooks, include_comments=False),
        {r: mentions(files, include_comments=False) - {r} for r, files in role_files.items()},
    )
    commented = reachable(
        mentions(playbooks, include_comments=True),
        {r: mentions(files, include_comments=True) - {r} for r, files in role_files.items()},
    )

    unused = [r for r in ROLES if r not in commented]
    for role in ROLES:
        if role in unused:
            print(f"UNUSED     {role}")
        elif role not in active:
            print(f"COMMENTED  {role}")

    if not unused:
        print("All good, every role is used by a playbook")
    return 1 if unused else 0


if __name__ == "__main__":
    sys.exit(main())

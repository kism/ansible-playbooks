#!/usr/bin/env -S uv run python
"""Compare Bitwarden Secrets Manager against this repo.

UNUSED    secret id not referenced anywhere in the repo
MISMATCH  secret name doesn't match the var that looks it up

Usage: $(./scripts/loadcreds) && ./scripts/bws_audit.py [project_id]
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".venv", ".git", "collections"}
VAR_RE = re.compile(r"^\s*-?\s*([A-Za-z0-9_]+):")


def normalise(name: str) -> str:
    # ponytail: naive match (lowercase, strip secret_, non-alnum -> _), add aliases if naming differs
    name = name.lower().removeprefix("secret_")
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")


def matches(key: str, var: str, loc: str) -> bool:
    key, var = normalise(key), normalise(var)
    if key == var:
        return True
    # Host specific secrets are named <var>_<hostname> in bws, e.g. secret_foo_pvpn in host_vars/pvpn.yml
    path = Path(loc.rsplit(":", 1)[0])
    return path.parent == Path("inventory/host_vars") and key == f"{var}_{normalise(path.stem)}"


def repo_lines() -> list[tuple[Path, int, str]]:
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            path = Path(root) / f
            try:
                lines = path.read_text().splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            out.extend((path, i, line) for i, line in enumerate(lines))
    return out


def var_name(lines: list[str], i: int) -> str:
    m = VAR_RE.match(lines[i])
    return m.group(1) if m else lines[i].strip()


def main() -> int:
    if not os.environ.get("BWS_ACCESS_TOKEN"):
        print("BWS_ACCESS_TOKEN not set, run: $(./scripts/loadcreds)", file=sys.stderr)
        return 1

    # bws CLI over bitwarden_sdk: the sdk's list() needs an organisation id, bws doesn't
    secrets = json.loads(
        subprocess.run(["bws", "secret", "list", *sys.argv[1:2], "-o", "json"], check=True, capture_output=True, text=True).stdout
    )

    all_lines = repo_lines()
    file_cache: dict[Path, list[str]] = {}
    problems = 0

    for s in secrets:  # only id + key are used, values are never printed
        sid, key = s["id"], s["key"]
        hits = [(p, i) for p, i, line in all_lines if sid in line]
        if not hits:
            print(f"UNUSED    {sid}  {key}")
            problems += 1
            continue
        refs = []
        for path, i in hits:
            lines = file_cache.setdefault(path, path.read_text().splitlines())
            refs.append((var_name(lines, i), f"{path.relative_to(REPO)}:{i + 1}"))
        # Same id can be used in several places, only a mismatch if none match
        if not any(matches(key, v, loc) for v, loc in refs):
            print(f"MISMATCH  {sid}  bws={key}  repo=" + ", ".join(f"{v} ({loc})" for v, loc in refs))
            problems += 1
    if not problems:
        print(f"All good, {len(secrets)} secrets checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env -S uv run python
"""Find facts used as top-level vars (ansible_default_ipv6) instead of ansible_facts['default_ipv6'].

ansible-core 2.24 stops injecting facts as top-level vars, and ansible.cfg already sets
inject_facts_as_vars = False, so these are undefined at runtime. ansible-lint has no rule for it.

Only Jinja is checked: {{ }} / {% %} in YAML strings and templates, plus bare-Jinja keys
like when: and that:. Plain YAML keys named ansible_* (debug labels) are fine.

Usage: ./scripts/injected_facts_audit.py
"""

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
JINJA_RE = re.compile(r"\{\{(.*?)\}\}|\{%(.*?)%\}", re.DOTALL)
STRING_RE = re.compile(r"'[^']*'|\"[^\"]*\"")  # literals like 'ansible_main' in group_names aren't vars
NAME_RE = re.compile(r"\bansible_[a-z0-9_]+\b")
BARE_JINJA_KEYS = {"when", "changed_when", "failed_when", "until", "that"}
# Connection, magic and inventory vars that are legitimately top-level
ALLOWED = {
    "ansible_facts", "ansible_host", "ansible_host_description", "ansible_port", "ansible_user",
    "ansible_connection", "ansible_python_interpreter", "ansible_managed", "ansible_check_mode",
    "ansible_diff_mode", "ansible_config_file", "ansible_search_path", "ansible_failed_result",
    "ansible_failed_task", "ansible_forks", "ansible_inventory_sources", "ansible_limit",
    "ansible_run_tags", "ansible_skip_tags", "ansible_verbosity", "ansible_version",
    "ansible_role_name", "ansible_role_names", "ansible_dependent_role_names", "ansible_collection_name",
}  # fmt: skip
ALLOWED_PREFIXES = ("ansible_become", "ansible_ssh", "ansible_play_", "ansible_loop", "ansible_parent_role")


def fact_names(expr: str) -> set[str]:
    names = set(NAME_RE.findall(STRING_RE.sub("", expr)))
    return {n for n in names if n not in ALLOWED and not n.startswith(ALLOWED_PREFIXES)}


def jinja_blocks(text: str) -> list[str]:
    return [a or b for a, b in JINJA_RE.findall(text)]


def walk(node: object, key: str = "") -> list[str]:
    """Every Jinja expression in a parsed YAML document."""
    if isinstance(node, dict):
        return [e for k, v in node.items() for e in walk(v, str(k))]
    if isinstance(node, list):
        return [e for v in node for e in walk(v, key)]
    if isinstance(node, str):
        return [node] if key in BARE_JINJA_KEYS else jinja_blocks(node)
    return []


def main() -> int:
    problems = 0
    yaml_files = [*REPO.glob("*.yml"), *(REPO / "roles").rglob("*.yml"), *(REPO / "inventory").rglob("*.yml")]
    for path in sorted(yaml_files):
        if path.name.endswith(".tmp.yml"):
            continue  # scratch, excluded from lint too
        expressions = walk(yaml.safe_load(path.read_text()))
        for name in sorted({n for e in expressions for n in fact_names(e)}):
            print(f"{path.relative_to(REPO)}: {name} -> ansible_facts['{name.removeprefix('ansible_')}']")
            problems += 1

    for path in sorted((REPO / "roles").glob("*/templates/**/*")):
        if path.is_file():
            for name in sorted({n for e in jinja_blocks(path.read_text()) for n in fact_names(e)}):
                print(f"{path.relative_to(REPO)}: {name} -> ansible_facts['{name.removeprefix('ansible_')}']")
                problems += 1

    if not problems:
        print("All good, no facts used as top-level vars")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

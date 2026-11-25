#!/usr/bin/env -S uv run python
"""Find docker compose stacks that won't get updated by maintenance_update.yml.

NO_UNIT     role has a docker-compose file but no systemd unit running `docker compose up`,
            so pulled images are never used (restart: always keeps the old container)
NOT_PULLED  stack dir isn't in the host's docker_compose_paths, so images are never pulled
STALE       docker_compose_paths entry that no role on the host deploys

Usage: ./scripts/compose_audit.py
"""

import re
import sys
from pathlib import Path

import jinja2
import yaml
from rich.console import Console
from rich.markup import escape

# soft_wrap: long lines stay on one line for grep and CI logs, highlight: only the colours below
console = Console(soft_wrap=True, highlight=False)

REPO = Path(__file__).resolve().parent.parent
ROLES = REPO / "roles"
INVENTORY = REPO / "inventory"
# Commented out roles are toggles in build playbooks, they're still deployed so count them
ROLE_LINE_RE = re.compile(r"^\s*#?\s*-\s*(?:role:\s*)?([a-z0-9_]+)\s*$", re.MULTILINE)
WORKDIR_RE = re.compile(r"^WorkingDirectory=(.+)$", re.MULTILINE)


def load_yaml(path: Path) -> dict:
    return (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}


def render(value: str, variables: dict) -> str:
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    for _ in range(5):  # vars can reference vars
        if "{{" not in value:
            break
        value = env.from_string(value).render(variables)
    return value


def norm(path: str) -> str:
    return path.rstrip("/")


def compose_units(role: Path) -> list[str]:
    """WorkingDirectory of every systemd unit in the role that runs `docker compose up`."""
    units = [
        p.read_text()
        for d in ("files", "templates")
        for p in (role / d).rglob("*")
        if p.name.endswith((".service", ".service.j2"))
    ]
    return [m.group(1).strip() for u in units if "compose up" in u for m in WORKDIR_RE.finditer(u)]


def main() -> int:
    docker_roles = {r.name for r in ROLES.iterdir() if any(r.rglob("docker-compose*"))}
    group_vars = load_yaml(INVENTORY / "group_vars/all.yml") | load_yaml(INVENTORY / "group_vars/ansible_main.yml")
    problems = 0

    for playbook in sorted(REPO.glob("build_*.yml")):
        # ponytail: build playbooks target one host, a group or a meta_ role including docker roles isn't followed
        host = yaml.safe_load(playbook.read_text())[0]["hosts"]
        host_vars = load_yaml(INVENTORY / f"host_vars/{host}.yml")
        compose_paths = {norm(p) for p in host_vars.get("docker_compose_paths", [])}
        roles = [r for r in ROLE_LINE_RE.findall(playbook.read_text()) if r in docker_roles]
        expected = set()

        for role in roles:
            role_dir = ROLES / role
            variables = group_vars | load_yaml(role_dir / "defaults/main.yml") | load_yaml(role_dir / "vars/main.yml") | host_vars
            variables["inventory_hostname"] = host
            dirs = compose_units(role_dir)
            if not dirs:
                console.print(f"[bold red]NO_UNIT[/]     {host:10} {role}")
                problems += 1
                continue
            for d in dirs:
                try:
                    d = norm(render(d, variables))
                except jinja2.UndefinedError as e:
                    console.print(f"[bold red]UNRESOLVED[/]  {host:10} {role}: {escape(d)} [dim]({escape(e.message)})[/]")
                    problems += 1
                    continue
                expected.add(d)
                if d not in compose_paths:
                    console.print(f"[bold red]NOT_PULLED[/]  {host:10} {role}: [dim]add[/] {d} [dim]to[/] [cyan]inventory/host_vars/{host}.yml[/] [dim]docker_compose_paths[/]")
                    problems += 1

        for path in sorted(compose_paths - expected):
            console.print(f"[bold yellow]STALE[/]       {host:10} {path} [dim]in docker_compose_paths, no role on this host deploys it[/]")
            problems += 1

    if not problems:
        console.print("[green]All good[/], every compose stack gets pulled and restarted")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

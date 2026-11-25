#!/usr/bin/env -S uv run python
"""Check every nginx vhost logs to its own files.

Each server block that serves something (has a location, or listens on 443) needs:
  access_log /var/log/nginx/vhosts/<name>.access   (fail2ban's nginx jails read vhosts/*.access)
  error_log  /var/log/nginx/vhosts/<name>.error
and no two server_names may share a log file. Port 80 blocks that only redirect are skipped.

Usage: ./scripts/nginx_logging_audit.py
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.markup import escape

# soft_wrap: long lines stay on one line for grep and CI logs, highlight: only the colours below
console = Console(soft_wrap=True, highlight=False)

REPO = Path(__file__).resolve().parent.parent
# ponytail: only sites-available/*.conf, configure_pve's single templated vhost isn't checked
SITE_GLOB = "roles/*/files/hosts/*/sites-available/*.conf"
LOG_DIR = "/var/log/nginx/vhosts/"
EXPECTED = {"access_log": ".access", "error_log": ".error"}


def server_blocks(text: str) -> list[str]:
    """Bodies of the top level server { } blocks, braces inside quotes are ignored."""
    text = re.sub(r"#[^\n]*", "", text)
    blocks, depth, start, quote = [], 0, None, None
    for i, ch in enumerate(text):
        if quote:
            quote = None if ch == quote else quote
        elif ch in "\"'":
            quote = ch
        elif ch == "{":
            if depth == 0 and re.search(r"\bserver\s*$", text[:i]):
                start = i + 1
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(text[start:i])
                start = None
    return blocks


def directive(body: str, name: str) -> str | None:
    """First argument of a directive at the server level (not inside a location)."""
    # Drop location bodies, innermost first, until no braces are left
    top_level, previous = body, None
    while top_level != previous:
        previous, top_level = top_level, re.sub(r"\{[^{}]*\}", "", top_level)
    m = re.search(rf"^\s*{name}\s+([^\s;]+)", top_level, re.MULTILINE)
    return m.group(1) if m else None


def main() -> int:
    files = sorted(REPO.glob(SITE_GLOB))
    if not files:
        console.print(f"[bold red]No vhost files found matching[/] {SITE_GLOB}")
        return 1

    problems = []
    used_by: dict[str, set[str]] = defaultdict(set)

    for path in files:
        rel = path.relative_to(REPO)
        for body in server_blocks(path.read_text()):
            if "location" not in body and not re.search(r"listen\s+\S*443", body):
                continue  # port 80 redirect block
            server_name = directive(body, "server_name") or "?"
            for name, suffix in EXPECTED.items():
                value = directive(body, name)
                if value is None:
                    problems.append(f"[bold red]MISSING[/]   [cyan]{rel}[/]: {escape(server_name)} has no {name}")
                elif value == "off" or not (value.startswith(LOG_DIR) and value.endswith(suffix)):
                    problems.append(f"[bold red]WRONG[/]     [cyan]{rel}[/]: {escape(server_name)} {name} {escape(value)}[dim], want {LOG_DIR}<name>{suffix}[/]")
                else:
                    used_by[value].add(server_name)

    problems += [
        f"[bold red]SHARED[/]    {escape(log)} is used by {', '.join(sorted(names))}" for log, names in sorted(used_by.items()) if len(names) > 1
    ]

    console.print("\n".join(problems) if problems else f"[green]All good[/], {len(files)} vhost files each log to their own files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

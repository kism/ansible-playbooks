#!/usr/bin/python3
"""Show how each nginx location is exposed: open to the internet, allowlistapp only, geofenced, or both.

Usage: sudo nginx_exposure            # parse the live config via `nginx -T`
       nginx_exposure site.conf ...      # parse files instead (e.g. the repo copies)

allowlist = `include /etc/nginx/ipallowlist.conf` (written by allowlistapp)
geofence  = `auth_request /_geoip` ($geoip_allowed, from maxmind_geoip_nginx)
With `satisfy any` either one lets a client in, otherwise both are required.
"""

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field

ALLOWLIST = "include /etc/nginx/ipallowlist.conf"
GEOFENCE = "auth_request /_geoip"


@dataclass
class Block:
    head: str
    file: str
    directives: list = field(default_factory=list)
    locations: list = field(default_factory=list)


def read_config(paths):
    if paths:
        return "".join("# configuration file " + p + ":\n" + open(p).read() for p in paths)
    return subprocess.run(["nginx", "-T"], check=True, capture_output=True, text=True).stdout


def parse(text):
    """Yield (file, server_names, location, access) for each non-internal location in a server listening on 80/443."""
    # ponytail: line-based comment stripping, a '#' inside a quoted string would cut the line. Fine for these configs.
    lines = []
    for line in text.splitlines():
        header = re.match(r"# configuration file (.+):$", line)
        if header:
            lines.append("@file " + header.group(1) + ";")
            continue
        lines.append(line.split("#", 1)[0])

    stack = []
    servers = []
    stmt = ""
    current_file = "?"
    for token in re.split(r"([{};])", "\n".join(lines)):
        if token == "{":
            stack.append(Block(" ".join(stmt.split()), current_file))
            stmt = ""
        elif token == ";":
            stmt = " ".join(stmt.split())
            if stmt.startswith("@file "):
                current_file = stmt[6:]
            elif stack:
                stack[-1].directives.append(stmt)
            stmt = ""
        elif token == "}":
            block = stack.pop()
            if block.head.startswith("location") and stack:
                # Attach to the enclosing server (or location, for nested ones)
                stack[-1].locations.append(block)
            elif block.head == "server":
                servers.append(block)
            stmt = ""
        else:
            stmt += token

    for server in servers:
        names = " ".join(d.split(None, 1)[1] for d in server.directives if d.startswith("server_name "))
        listens = [d for d in server.directives if d.startswith("listen ")]
        if not any(re.search(r"\b(80|443)\b", d) for d in listens):
            continue
        if not server.locations:
            continue  # Redirect-only / return-only server blocks
        for loc in server.locations:
            directives = server.directives + loc.directives  # Server-level includes are inherited
            if "internal" in loc.directives:
                continue
            allow = ALLOWLIST in directives
            geo = GEOFENCE in directives
            if allow and geo:
                access = "geofence OR allowlist" if "satisfy any" in directives else "geofence AND allowlist"
            elif allow:
                access = "allowlist"
            elif geo:
                access = "geofence"
            else:
                access = "OPEN"
            yield os.path.basename(server.file), names, loc.head[len("location"):].strip(), access


def main():
    rows = sorted(parse(read_config(sys.argv[1:])), key=lambda r: (r[3] != "OPEN", r[1], r[2]))
    if not rows:
        sys.exit("No server locations found")
    width_name = max(len(r[1]) for r in rows)
    width_loc = min(max(len(r[2]) for r in rows), 40)
    print(f"{'ACCESS':<24} {'SERVER':<{width_name}} {'LOCATION':<{width_loc}} FILE")
    for file, names, location, access in rows:
        if len(location) > width_loc:
            location = location[: width_loc - 3] + "..."
        print(f"{access:<24} {names:<{width_name}} {location:<{width_loc}} {file}")


if __name__ == "__main__":
    main()

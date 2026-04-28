#!/usr/bin/env python3

import json
from urllib.request import urlopen
from datetime import datetime

ANSIBLE_JSON_URL = (
    "https://cmdb.kierangee.au/inventory/kism_main/group/ansible_main/json"
)

with urlopen(ANSIBLE_JSON_URL) as response:
    data = json.loads(response.read())


def build_motd_table(data):
    """Build ASCII table from host data"""
    magenta = "\033[35m"
    reset = "\033[0m"

    def format_cell(hostname, description, width):
        visible_text = f"{hostname}, {description}"[:width]
        host_visible_len = min(len(hostname), len(visible_text))
        colored_host = f"{magenta}{visible_text[:host_visible_len]}{reset}"
        remainder = visible_text[host_visible_len:]
        return colored_host + remainder + (" " * (width - len(visible_text)))

    hosts = []

    for hostname, host_data in data.items():
        if isinstance(host_data, dict):
            description = host_data.get("ansible_host_description", "")
            if description:
                hosts.append((hostname, description))

    # Sort by hostname
    hosts.sort(key=lambda x: x[0])

    if not hosts:
        return ""

    # Fixed table width is 76 characters including indent.
    # Row format: "   | <left cell> | <right cell> |"
    # Total: 10 + left_width + right_width = 76, so widths must sum to 66.
    left_width = 33
    right_width = 33

    # Build table
    lines = []
    lines.append("   +" + "-" * 71 + "+")

    for i in range(0, len(hosts), 2):
        left = format_cell(hosts[i][0], hosts[i][1], left_width)
        if i + 1 < len(hosts):
            right = format_cell(hosts[i + 1][0], hosts[i + 1][1], right_width)
        else:
            right = " " * right_width
        lines.append(f"   | {left} | {right} |")

    lines.append("   +" + "-" * 71 + "+")

    return "\n".join(lines)


MOTD_INTRO = r"""Art by jgs / Joan Stark

































































































  ,--.                         .       *             .        .
  |  |,-.  ,---.        .         .             *                    *
  |     / | .-. |              _    .  ,   .           .
  |  \  \ ' '-' '.--.      *  / \_ *  / \_      _  *        *   /\'__        *
  `--'`--'.`-  / '--'        /    \  /    \,   ((        .    _/  /  \  *'.
  ,--.    `---'         .   /\/\  /\/ :' __ \_  `          _^/  ^/    `--.
  |  | ,--,--.,--,--,      /    \/  \  _/  \-'\      *    /.' ^_   \_   .'\  *
  |  |' ,-.  ||      \   /\  .-   `. \/     \ /==~=-=~=-=-;.  _/ \ -. `_/   \
  |  |\ '-'  ||  ||  |  /  `-.__ ^   / .-'.--\ =-=~_=-=~=^/  _ `--./ .-'  `-
  `--' `--`--'`--''--' /        `.  / /       `.~-^=-=~=^=.-'      '-._ `._
"""


motd_content = "Generated: " + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S") + " | " + MOTD_INTRO + "\n" + build_motd_table(data) + "\n"
print(motd_content)

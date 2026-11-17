#!/opt/pvpn-select/.venv/bin/python
"""Pick a Proton VPN server for the wg0 exit node and swap to it live.

Usage: sudo pvpn-select [country code]
"""

import getpass
import json
import os
import random
import re
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path

from proton.session import Session
from proton.session.exceptions import ProtonAPIAuthenticationNeeded

# Proton rejects old app versions. The official cli sends linux-vpn-cli@<proton-vpn-api-core version>+<arch>,
# so mirror that from api-core's versions.yml (first line is "version: X.Y.Z").
VERSIONS_URL = "https://raw.githubusercontent.com/ProtonVPN/python-proton-vpn-api-core/stable/versions.yml"
with urllib.request.urlopen(VERSIONS_URL, timeout=10) as resp:
    APPVERSION = f"linux-vpn-cli@{resp.readline().decode().split()[1]}+{platform.machine()}"
SESSION_FILE = Path("/opt/pvpn-select/session.json")
WG_CONF = Path("/etc/wireguard/wg0.conf")
SECURE_CORE, P2P, STREAMING = 1, 4, 8
SHOWN = 25


def save(session: Session) -> None:
    SESSION_FILE.touch(mode=0o600)
    SESSION_FILE.write_text(json.dumps(session.__getstate__()))


def login() -> Session:
    session = Session(appversion=APPVERSION, user_agent="pvpn-select")
    if not session.authenticate(input("Proton username: "), getpass.getpass("Password: ")):
        sys.exit("Login failed")
    if session.needs_twofa and not session.provide_2fa(input("2FA code: ")):
        sys.exit("2FA failed")
    save(session)
    return session


def get_session() -> Session:
    if not SESSION_FILE.exists():
        return login()
    session = Session(appversion=APPVERSION, user_agent="pvpn-select")
    session.__setstate__(json.loads(SESSION_FILE.read_text()))
    try:
        session.api_request("/vpn/v2")  # Cheap check, also refreshes the access token if expired
    except ProtonAPIAuthenticationNeeded:
        return login()
    return session


def main() -> None:
    if os.geteuid() != 0:
        sys.exit("Run with sudo, this changes wg0")

    session = get_session()
    max_tier = session.api_request("/vpn/v2")["VPN"]["MaxTier"]
    logicals = session.api_request("/vpn/v1/logicals", params={"SecureCoreFilter": "all"})["LogicalServers"]
    save(session)  # Tokens may have been refreshed

    country = (sys.argv[1] if len(sys.argv) > 1 else input("Country code (blank for all): ")).strip().upper()
    servers = sorted(
        (
            s
            for s in logicals
            if s["Status"] == 1
            and s["Tier"] <= max_tier
            and not s["Features"] & SECURE_CORE
            and (not country or s["ExitCountry"] == country)
        ),
        key=lambda s: s["Score"],  # Proton's own ranking, lower is better
    )[:SHOWN]
    if not servers:
        sys.exit(f"No servers for {country or 'any country'}")

    for i, s in enumerate(servers, 1):
        flags = " ".join(f for bit, f in ((P2P, "p2p"), (STREAMING, "stream")) if s["Features"] & bit)
        print(f"{i:>3}  {s['Name']:<12} {s.get('City') or '':<18} load {s['Load']:>3}%  {flags}")

    choice = input(f"Pick 1-{len(servers)} [1]: ").strip() or "1"
    logical = servers[int(choice) - 1]
    physical = random.choice([p for p in logical["Servers"] if p["Status"] == 1])
    endpoint = f"{physical['EntryIP']}:51820"
    pubkey = physical["X25519PublicKey"]

    # Persist for the next wg0 restart, the role templates wg0.conf with force: false so this sticks
    conf = WG_CONF.read_text()
    conf = re.sub(r"^PublicKey = .*$", f"PublicKey = {pubkey}", conf, flags=re.MULTILINE)
    conf = re.sub(r"^Endpoint = .*$", f"Endpoint = {endpoint}", conf, flags=re.MULTILINE)
    WG_CONF.write_text(conf)

    # Swap the peer live, restarting wg-quick would also restart tailscaled (Requires=)
    old_peers = subprocess.run(["wg", "show", "wg0", "peers"], check=True, capture_output=True, text=True).stdout.split()
    subprocess.run(
        ["wg", "set", "wg0", "peer", pubkey, "endpoint", endpoint, "allowed-ips", "0.0.0.0/0", "persistent-keepalive", "25"],
        check=True,
    )
    for old in old_peers:
        if old != pubkey:
            subprocess.run(["wg", "set", "wg0", "peer", old, "remove"], check=True)

    print(f"Now on {logical['Name']} ({endpoint}). Check the handshake with: wg show wg0 latest-handshakes")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Point the A and AAAA records for CF_RECORD at this host's public IPv4 and IPv6."""

from __future__ import annotations

import json
import os
import urllib.request

ZONE = os.environ["CF_ZONE_ID"]
TOKEN = os.environ["CF_API_TOKEN"]
RECORD = os.environ["CF_RECORD"]
API = f"https://api.cloudflare.com/client/v4/zones/{ZONE}/dns_records"


def cf(method: str, url: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def main() -> None:
    for rtype, ip_url in (("A", "https://api.ipify.org"), ("AAAA", "https://api6.ipify.org")):
        try:
            with urllib.request.urlopen(ip_url, timeout=10) as r:
                ip = r.read().decode().strip()
        except OSError as e:
            # ponytail: no public address of this family = leave the record alone
            print(f"{rtype}: no public ip ({e}), skipping")
            continue

        existing = cf("GET", f"{API}?type={rtype}&name={RECORD}")["result"]
        body = {"type": rtype, "name": RECORD, "content": ip, "ttl": 120, "proxied": False}
        if not existing:
            cf("POST", API, body)
            print(f"{rtype}: created {ip}")
        elif existing[0]["content"] != ip:
            cf("PUT", f"{API}/{existing[0]['id']}", body)
            print(f"{rtype}: {existing[0]['content']} -> {ip}")
        else:
            print(f"{rtype}: {ip} unchanged")


if __name__ == "__main__":
    main()

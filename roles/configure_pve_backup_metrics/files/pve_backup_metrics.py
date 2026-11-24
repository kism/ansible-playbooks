#!/usr/bin/env python3
"""Push Proxmox backup health for this node to VictoriaMetrics.

Checks outcomes, not events: a job that silently stops running (scheduler off, quorum loss)
never fires a failure notification, but its newest backup keeps getting older.

Metrics, all labelled with node:
  pve_backup_newest_timestamp_seconds{job,storage,vmid,name}  0 = expected but no backup found
  pve_backup_newest_size_bytes{job,storage,vmid,name}
  pve_backup_job_enabled{job,storage}
  pve_backup_job_ok{job}                                      last run's result was OK
  pve_backup_job_last_start_timestamp_seconds{job}            0 = never ran
  pve_backup_storage_used_ratio{storage}
  pve_backup_storage_active{storage}
  pve_backup_not_backed_up{vmid,name}                         guests in no backup job (cluster wide)
  pve_backup_scheduler_active                                 pvescheduler is running
  pve_backup_metrics_last_run_timestamp_seconds               alert if stale, the timer stopped

Run with --self-test to check the parsing, --dry-run to print instead of push.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

NODE = os.uname().nodename.split(".")[0]


def pvesh(path: str, *args: str) -> Any:  # shape depends on the endpoint
    out = subprocess.run(
        ["pvesh", "get", path, "--output-format", "json", *args], check=True, capture_output=True, text=True
    ).stdout
    return json.loads(out)


def parse_jobs(text: str) -> dict[str, dict[str, str]]:
    """/etc/pve/jobs.cfg vzdump sections -> {job_id: {option: value}}."""
    jobs: dict[str, dict[str, str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("vzdump:"):
            current = jobs.setdefault(line.split(":", 1)[1].strip(), {})
        elif not line.strip() or not line[0].isspace():
            current = None  # blank line or another job type ends the section
        elif current is not None:
            key, _, value = line.strip().partition(" ")
            current[key] = value.strip()
    return jobs


def upid_start(upid: str) -> int:
    """UPID:node:pid:pstart:starttime:type:id:user: -> starttime (hex) as unix seconds."""
    return int(upid.split(":")[4], 16)


def expected_vmids(job: dict[str, str], local_guests: set[int]) -> set[int]:
    """Guests this node should back up for the job, vzdump only touches guests on its own node."""
    if job.get("all") == "1":
        exclude = {int(v) for v in job.get("exclude", "").split(",") if v}
        return local_guests - exclude
    return {int(v) for v in job.get("vmid", "").split(",") if v} & local_guests


def metric(metric_name: str, value: float, /, **labels: object) -> str:
    """Prometheus text format line, positional-only so a `name` label doesn't collide."""
    labels = {"node": NODE, **labels}
    esc = lambda v: str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'{metric_name}{{{",".join(f"{k}=\"{esc(v)}\"" for k, v in labels.items())}}} {value}'


def collect() -> list[str]:
    lines: list[str] = []
    guests = pvesh("/cluster/resources", "--type", "vm")
    names = {g["vmid"]: g.get("name", "") for g in guests}
    local_guests = {g["vmid"] for g in guests if g.get("node") == NODE and not g.get("template")}

    storages = {s["storage"]: s for s in pvesh(f"/nodes/{NODE}/storage", "--content", "backup")}
    for s in storages.values():
        lines.append(metric("pve_backup_storage_active", int(bool(s.get("active"))), storage=s["storage"]))
        if s.get("active"):
            lines.append(metric("pve_backup_storage_used_ratio", s.get("used_fraction", 0), storage=s["storage"]))

    contents: dict[str, list[dict]] = {}
    jobs_cfg = Path("/etc/pve/jobs.cfg")
    jobs = parse_jobs(jobs_cfg.read_text()) if jobs_cfg.exists() else {}
    for job_id, job in jobs.items():
        if job.get("node", NODE) != NODE:
            continue  # pinned to another node, that node reports it
        storage = job.get("storage", "")
        lines.append(metric("pve_backup_job_enabled", int(job.get("enabled", "1") == "1"), job=job_id, storage=storage))

        state_file = Path(f"/var/lib/pve-manager/jobs/vzdump-{job_id}.json")
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        lines.append(metric("pve_backup_job_ok", int(state.get("msg") == "OK"), job=job_id))
        upid = state.get("upid", "")
        lines.append(metric("pve_backup_job_last_start_timestamp_seconds", upid_start(upid) if upid else 0, job=job_id))

        if storage not in contents:
            try:
                contents[storage] = pvesh(f"/nodes/{NODE}/storage/{storage}/content", "--content", "backup")
            except subprocess.CalledProcessError:
                contents[storage] = []  # storage down or missing, every guest reads as 0 and alerts
        for vmid in sorted(expected_vmids(job, local_guests)):
            backups = [b for b in contents[storage] if b.get("vmid") == vmid]
            newest = max(backups, key=lambda b: b["ctime"], default={"ctime": 0, "size": 0})
            labels = {"job": job_id, "storage": storage, "vmid": vmid, "name": names.get(vmid, "")}
            lines.append(metric("pve_backup_newest_timestamp_seconds", newest["ctime"], **labels))
            lines.append(metric("pve_backup_newest_size_bytes", newest.get("size", 0), **labels))

    for g in pvesh("/cluster/backup-info/not-backed-up"):
        lines.append(metric("pve_backup_not_backed_up", 1, vmid=g["vmid"], name=g.get("name", "")))

    scheduler = subprocess.run(["systemctl", "is-active", "--quiet", "pvescheduler"], check=False).returncode == 0
    lines.append(metric("pve_backup_scheduler_active", int(scheduler)))
    lines.append(metric("pve_backup_metrics_last_run_timestamp_seconds", int(time.time())))
    return lines


def push(lines: list[str]) -> None:
    req = urllib.request.Request(
        f"{os.environ['VM_URL']}/api/v1/import/prometheus",
        data=("\n".join(lines) + "\n").encode(),
        headers={"Authorization": f"Bearer {os.environ['VM_TOKEN']}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        r.read()


def self_test() -> None:
    cfg = (
        "vzdump: backup-a\n\tschedule mon 01:00\n\tenabled 1\n\tnode pvematt\n\tstorage S1\n\tvmid 100,105\n\n"
        "realmsync: other\n\tschedule daily\n\n"
        "vzdump: backup-b\n\tall 1\n\texclude 101\n\tstorage S2\n"
    )
    jobs = parse_jobs(cfg)
    assert set(jobs) == {"backup-a", "backup-b"}, jobs
    assert jobs["backup-a"]["vmid"] == "100,105" and jobs["backup-a"]["node"] == "pvematt"
    assert "schedule" not in jobs["backup-b"]  # realmsync options didn't leak in
    assert expected_vmids(jobs["backup-a"], {100, 101}) == {100}  # 105 lives on the other node
    assert expected_vmids(jobs["backup-b"], {100, 101, 102}) == {100, 102}
    assert upid_start("UPID:pvewill:002FF2E6:05CEEFD4:6A0A0222:vzdump::root@pam:") == 0x6A0A0222
    assert metric("m", 1, name='a"b') == f'm{{node="{NODE}",name="a\\"b"}} 1'
    print("self-test ok")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif "--dry-run" in sys.argv:
        print("\n".join(collect()))
    else:
        push(collect())

# Kieran's Ansible Playbooks

[![Ansible Lint](https://github.com/kism/ansible-playbooks/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/kism/ansible-playbooks/actions/workflows/ansible-lint.yml)
[![Ansible Taste](https://github.com/kism/ansible-playbooks/actions/workflows/ansible-taste.yml/badge.svg)](https://github.com/kism/ansible-playbooks/actions/workflows/ansible-taste.yml)

Install collections

```bash
ansible-galaxy collection install --requirements-file collections/requirements.yml --upgrade
```

Running on macos
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

Load Bitwarden Secrets Manager credentials (needed for the `secret_*` lookups)
`$(./scripts/loadcreds)`

Run
`ansible-playbook build_ent.yml -i inventory/main.yml`

Run without server onboarding block
`ansible-playbook build_ent.yml -i inventory/main.yml --extra-vars "skip_onboard=true"`

## Scripts

| Script                 | What it do                                                                                         |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| `scripts/loadcreds`    | Prompt for and export `BWS_ACCESS_TOKEN`, use with `$(./scripts/loadcreds)`                        |
| `scripts/bws_audit.py` | List Bitwarden secrets not used in this repo, or whose name doesn't match the var that looks it up |
| `scripts/compose_audit.py` | List docker compose stacks that `maintenance_update.yml` won't pull or restart |
| `scripts/unused_roles_audit.py` | List roles no playbook uses, and roles only used in commented out lines |
| `scripts/nginx_logging_audit.py` | Check every nginx vhost logs to its own `vhosts/<name>.access` and `.error` file (fail2ban reads these) |

## Good style things to do

- Comment every one of those code quality searches when used
- Comment ever changed_when
- No hardcoded domain names, dns names
- Use creates/removes in ansible.builtin.cmd
- Use argv in ansible.builtin.cmd
- Naming:

| Role Prefix        | What it do                                                      |
| ------------------ | --------------------------------------------------------------- |
| configure\_        | (Install and) configure a specific thing                        |
| configure*service* | (Install and) configure something that will be/run as a service |
| create\_           | Create a new vm/ct/instance/whatever                            |
| uninstall\_        | Remove a specific application or package                        |
| maintenance\_      | No changes, other than patching                                 |
| meta\_             | roles that only include roles                                   |

| Playbook Prefix | What it mean                                        |
| --------------- | --------------------------------------------------- |
| adhoc\_         | Reference or adhoc playbooks, often don't keep them |
| audit\_         | Playbooks that get the state of VMs                 |
| build\_         | Build a VM                                          |
| configure\_     | Apply a configure\_ role or two to some VMs         |
| maintenance\_   | No changes, other than patching                     |

## Known workarounds

Things that work around someone else's bug or limitation. Check each one now and then, and remove the workaround once it's no longer needed.

- **NetworkManager IPv6 warnings silenced** (`configure_misc`, `/etc/NetworkManager/conf.d/99-quiet-ip6.conf`, added 2026-11-24)
  - Why: libndp sends router solicitations with `sa_family=AF_UNSPEC`, and the PVE 7.0 kernel rejects that. NM logs `failure sending router solicitation: Address family not supported by protocol (97)` about every minute. Harmless, because RAs still arrive unsolicited.
  - Check: on one host, `nmcli general logging domains DEFAULT` then `journalctl -u NetworkManager -f | grep solicit` for a few minutes. Quiet = fixed, delete the task and the file.
- **OPNsense syslog split on `local0`** (`configure_opnsense_syslog`, added 2026-11-24)
  - Why: OPNsense can only include programs or facilities, not exclude them. `filterlog` (firewall) and `kea-dhcp4` both log on `local0`, so they get their own destinations, and any other program that ends up on `local0` gets dropped silently.
  - Check, after OPNsense major upgrades, in the OPNsense shell: `cat /var/log/*/latest.log | awk '{p=substr($1,2,index($1,">")-2); print int(p/8), $4}' | sort | uniq -c | sort -rn`. Anything on facility 16 other than `filterlog`/`kea-dhcp4` needs adding to the local0 destination.
- **Vector GeoIP data only refreshes on restart** (`configure_docker_victoriametrics`, `vector.yaml`, added 2026-11-24)
  - Why: Vector loads `GeoLite2-City.mmdb` once at startup. `geoipupdate` downloads a new one every 72h, but Vector keeps using the old one until the stack restarts (reboot, image update, role run).
  - Check: if Vector learns to reload enrichment tables on file change, drop this. Until then, geo data can be a few weeks stale, which is fine for a world map.
- **vmauth legacy unprefixed paths** (`configure_docker_victoriametrics/templates/auth.yml.j2`, rproxy `vic.conf`, added 2026-11-24)
  - Why: everything moved to `/metrics`, `/logs` and `/firewall`, but OPNsense and Home Assistant push metrics to the old root path through their own UIs, and bigbilly is often offline.
  - Check: point OPNsense and Home Assistant at `<vmauth>/metrics`, re-run `configure_journal_upload` on bigbilly, then delete the `ponytail: legacy` routes in `auth.yml.j2` and the old `/insert/journald/` location in `vic.conf`.

## Todo

- Separate role for certbot setup
- Figure out ssd biggest users

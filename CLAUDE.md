# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Homelab Ansible playbooks. Single author, single inventory, run from a workstation.

## Commands

Tooling lives in the uv venv (`.venv/`); `ansible-lint` is not on the system PATH.

```bash
uv sync                                    # install python deps (ansible, ansible-lint, ansible-taste, bitwarden-sdk)
ansible-galaxy collection install --requirements-file collections/requirements.yml --upgrade
$(./zz_loadcreds)                          # export BWS_ACCESS_TOKEN for bitwarden secret lookups

.venv/bin/ansible-lint                     # lint everything (strict mode, what CI runs)
.venv/bin/ansible-lint roles/<role_name>   # lint one role
.venv/bin/ansible-taste                    # style checker, also run in CI

ansible-playbook build_<host>.yml -i inventory/main.yml
ansible-playbook build_<host>.yml -i inventory/main.yml --extra-vars "skip_onboard=true"  # skip meta_onboard roles
```

There are no tests; ansible-lint (`strict: true`, see `.ansible-lint`) and ansible-taste are the checks. `*.tmp.yml` files are excluded from lint and are scratch.

## Architecture

- **Playbooks are thin**: top-level `build_<host>.yml` targets one inventory host and just lists roles. All logic is in `roles/`. Commented-out roles in a build playbook are intentional toggles (e.g. `create_proxmox_ct`, `create_opnsense_entries` only needed on first build).
- **Typical build order**: `maintenance_gather_facts` → `meta_onboard` (package manager, packages, users, misc, sshd, locale, firewall, motd) → purpose-specific `configure_*` roles → optionally `configure_telegraf` / `configure_wazuh_agent`.
- **Facts are not gathered by default** (`gather_facts = False` in `ansible.cfg`); roles that need facts rely on `maintenance_gather_facts` running first.
- **Multi-distro**: hosts are a mix of dnf, apt and pacman. Roles branch on package manager / virtualization role, e.g. `configure_packages/vars/{all,baremetal}-{apt,dnf,pacman,common}.yml`.
- **Secrets**: all secrets are `secret_*` vars in `inventory/group_vars/all.yml`, resolved via `bitwarden.secrets.lookup` (needs `BWS_ACCESS_TOKEN`). Never hardcode secrets or domain names; use `homelab_domain_internal` / `homelab_domain_external`.
- **Containers**: dockerised services (e.g. headscale) drop a `docker-compose.yml` into `/opt/<name>` and run it via a custom systemd unit in the role's `files/`.
- Remote user is `ansible_svc`; `become: true` is set at play level.

## Naming

Roles: `configure_` (install+configure a thing), `create_` (new VM/CT/DNS entry), `remove_`/`uninstall_`, `maintenance_` (no changes beyond patching), `meta_` (only includes other roles).
Playbooks: `build_` (build a host), `configure_` (apply a role to some hosts), `audit_` (read state), `maintenance_`, `adhoc_` (throwaway/reference).

Prefix registered vars with the role name (e.g. `configure_firewall_pve_status`).

## Style rules (from README)

- Every `changed_when`, `failed_when: false`, `ignore_errors`, and lint skip needs a trailing comment explaining why.
- Don't add `become: true` on tasks when the play already has it; don't add `owner: root`/`group: root` redundantly with `become_user: root`.
- `ansible.builtin.command`: use `argv` and `creates`/`removes`.
- Mark deliberate shortcuts with a `# ponytail:` comment.

## Firewalld

- Always open ports via a firewalld service XML file, never `ansible.posix.firewalld` with `port:`.
  - Put the XML in the role's `files/firewalld/<name>.xml`, copy the `firewalld/` dir to `/etc/firewalld/services/`, notify `Reload firewalld`, flush handlers, then enable it with `ansible.posix.firewalld: service: <name>`.
  - Example: `roles/configure_headscale`.
- `configure_firewall` skips Proxmox hosts (no firewalld on PVE).

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

## Code Quality

### Code quality searches

Searches for vscode to find code quality issues that don't get caught by ansible-lint

```text
# failed_when: false without a comment
failed_when: false[^#]*$

# changed_when: true, false without a comment
changed_when: \b(?:true|false)\b[^#]*$

# ignore_errors in any context
ignore_errors:

# skip_ansible_lint in any context
skip_ansible_lint

# Unecessary become true by itself
^.*become: true.*$\n.*\..*\..*:

# Unecessary chown/chgrp
^.*become: true$.*$\n^.*become_user: root.*$

# Unecessary chown/chgrp
^.*owner: root$.*$\n^.*group: root.*$

# Commented out tasks and such
\# - name

# Tasks with same name
<no regex yet>
```

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

## Todo

- Separate role for certbot setup

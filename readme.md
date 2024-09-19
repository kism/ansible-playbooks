# Kieran's Ansible Playbooks

Install collections

```bash
ansible-galaxy collection install -r collections/requirements.yml --upgrade
```

Running on macos
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

Run
`ansible-playbook build_ent.yml -i inventory.yml`

Run without server onboarding block
`ansible-playbook build_ent.yml -i inventory.yml --extra-vars "skip_onboard=true"`

## Vault

No need for `--vault-password-file=/tmp/ansiblevaultpassword` since its in config

Ensure the secrets repo is cloned

```bash
touch /tmp/ansiblevaultpassword && chmod 600 /tmp/ansiblevaultpassword && echo password > /tmp/ansiblevaultpassword
ansible-vault encrypt ../ansible-playbooks-secrets/secrets*
ansible-vault decrypt ../ansible-playbooks-secrets/secrets*
```

## Code Quality

### Code quality searches

```text
```

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

### Good style things to do

* Comment every one of those code quality searches when used
* Comment ever changed_when
* No hardcoded domain names, dns names
* Use creates/removes in ansible.builtin.cmd
* Use argv in ansible.builtin.cmd
* Naming:

| Role Prefix        | What it do                                                         |
|--------------------|--------------------------------------------------------------------|
| configure_         | (Install and) configure a specific thing                           |
| configure_service_ | (Install and) configure something that will be/run as a service    |
| create_            | Create a new vm/ct/instance/whatever                               |
| uninstall_         | Remove a specific application or package                           |
| maintenance_       | No changes, other than patching                                    |
| meta_              | roles that only include roles                                      |

| Playbook Prefix | What it mean                                        |
|-----------------|-----------------------------------------------------|
| adhoc_          | Reference or adhoc playbooks, often don't keep them |
| audit_          | Playbooks that get the state of VMs                 |
| build_          | Build a VM                                          |
| configure_      | Apply a configure_ role or two to some VMs          |
| maintenance_    | No changes, other than patching                     |

## TODO

* Proxmox
  * Proxmox Set IP address, MAC in DNS, DHCP in opnsense
        <https://docs.opnsense.org/development/api/core/unbound.html>
        <https://docs.opnsense.org/development/api/core/kea.html>
  * Proxmox grab lxc <https://images.linuxcontainers.org/>
* Unmount, chmod, remount disks to ensure perms
* ~~GNU stow for dotfiles~~
* github gpg key
* get rid of dotfiles repo, setup for workstation one role plus meta role for non-servers
* setup cert
* workstation setup
* ~~make repo for kierangee.au~~
* better server packages install
* figure out configure_concept_baremetal

## do ~~later~~ never

```bash
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows```

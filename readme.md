# Kieran's Ansible Playbooks

Install collections

```bash
ansible-galaxy collection install -r requirements.yml --upgrade
```

Running on macos
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

Run
`ansible-playbook build_ent.yml -i inventory.yml --user ansible_svc -e @../archivepodcastsecrets/secrets.yml --vault-password-file=/tmp/ansiblevaultpassword`

`ansible-playbook build_podc-test.yml -i inventory.yml --user ansible_svc -e @../archivepodcastsecrets/secrets.yml -e @../archivepodcastsecrets/secrets_podc-test.yml --vault-password-file=/tmp/ansiblevaultpassword`

## Vault

```bash
touch /tmp/ansiblevaultpassword && chmod 600 /tmp/ansiblevaultpassword && echo password > /tmp/ansiblevaultpassword
ansible-vault encrypt ../archivepodcastsecrets/secrets* # No need for --vault-password-file=/tmp/ansiblevaultpassword since its in config
ansible-vault decrypt ../archivepodcastsecrets/secrets*
```

## Code Quality

### Code quality searches

```text
failed_when: false
ignore_errors: true
skip_ansible_lint
```

### Good style things to do

* Comment every one of those code quality searches when used
* Comment ever changed_when
* No hardcoded domain names, dns names
* Use creates/removes in ansible.builtin.cmd
* Use argv in ansible.builtin.cmd
* Naming:

| Role Prefix  | What it do                                                         |
|--------------|--------------------------------------------------------------------|
| configure_   | (Install and) configure a specific thing                           |
| install_     | Install a specific thing, generally can't be configured in ansible |
| uninstall_   | Remove a specific application or package                           |
| maintenance_ | No changes, other than patching                                    |
| meta_        | roles that only include roles                                      |

| Playbook Prefix | What it mean                                        |
|-----------------|-----------------------------------------------------|
| adhoc_          | Reference or adhoc playbooks, often don't keep them |
| audit_          | Playbooks that get the state of VMs                 |
| build_          | Build a VM                                          |
| maintenance_    | No changes, other than patching                     |

## TODO

* separate out sab
* separate out more configs
* set permissions on unmounted directories
* Proxmox
* Proxmox `pct push`
* Proxmox Set IP address, MAC in DNS, DHCP in opnsense
* Proxmox grab lxc https://images.linuxcontainers.org/
* Unmount, chmod, remount disks to ensure perms
* Do true config.d telegraf, only base config in the configure_telegraf role
  * Do an adhoc clean of all telegraf.d directories
* GNU stow for dotfiles

do later

```bash
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows```

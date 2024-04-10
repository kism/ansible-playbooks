# Kieran's Ansible Playbooks

Install collections

```bash
ansible-galaxy collection install -r requirements.yml
```

Running on macos
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

Run
`ansible-playbook build_ent.yml -i inventory.yml --user ansible_svc -e @../archivepodcastsecrets/secrets.yml --vault-password-file=/tmp/ansiblevaultpassword`

`ansible-playbook build_podc-test.yml -i inventory.yml --user ansible_svc -e @../archivepodcastsecrets/secrets.yml -e @../archivepodcastsecrets/secrets_podc-test.yml --vault-password-file=/tmp/ansiblevaultpassword`

## Vault

```bash
echo password > /tmp/ansiblevaultpassword
ansible-vault encrypt ../archivepodcastsecrets/secrets* --vault-password-file=/tmp/ansiblevaultpassword
ansible-vault decrypt ../archivepodcastsecrets/secrets* --vault-password-file=/tmp/ansiblevaultpassword
```

## Code quality searches

```text
failed_when: false
ignore_errors: true
skip_ansible_lint
```

## todo

* separate out sab
* use creates for ansible.builtin.command
* Use argv for multiline commands
* separate out more configs
* make username kism a variable
* fix ent domain, do domains everywhere
* configure vs install roles
* role that includes roles for the first section meta_something
* prettier config?
* use that dumb way of breaking up urls

do later

```bash
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows```

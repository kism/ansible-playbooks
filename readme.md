# Kieran's Ansible Playbooks

* change shell to command in mosts cases???
* better ffmpeg install
* make username kism a variable

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


do later

```bash
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows```
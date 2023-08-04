# Kieran's Ansible Playbooks

* reorg folders
* make real roles
* change shell to command in mosts cases???
* better ffmpeg install
* set root password with hash in secrets
* set kism password with hash in secrets
* remove backup_svc's password once router is replaced
* make username kism a variable
* make telegraf config work with ansible_hostname

Install collections

```bash
ansible-galaxy collection install community.general
```


Running on macos
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

Run
`ansible-playbook build_ent.yml -i inventory.yml --user ansible_svc -e @secrets.yml`

`ansible-playbook build_podc-test.yml -i inventory.yml --user ansible_svc -e @secrets.yml -e @secrets_podc-test.yml`

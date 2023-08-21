# Kieran's Ansible Playbooks

* change shell to command in mosts cases???
* better ffmpeg install
* make username kism a variable

Install collections

```bash
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows
```


Running on macos
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

Run
`ansible-playbook build_ent.yml -i inventory.yml --user ansible_svc -e @secrets.yml`

`ansible-playbook build_podc-test.yml -i inventory.yml --user ansible_svc -e @secrets.yml -e @secrets_podc-test.yml`

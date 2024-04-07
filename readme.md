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

## todo

* better ffmpeg install
* separate out sab
* make username kism a variable
* virtualisation check?? use baremetal group
* fix ent domain, do domains everywhere
* configure vs install roles
* role that includes roles for the first section meta_something
* prettier config?
* replace instances of `ansible_architecture == '` with map

```yaml
vars:
    arch_map: # uname (ansible), whatever ffmpeg uses
        x86_64: amd64
        aarch64: arm64
        armv6l: armel
        armv7l: armel
        armv8l: armel
    ffmpeg_arch: ""

tasks:
- name: Get ffmpeg_arch
    block:
    - name: Set target arch per map if possible
        ansible.builtin.set_fact:
        ffmpeg_arch: "{{  arch_map[ansible_architecture] }}"

    rescue:
    - name: Set default ffmpeg_arch
        ansible.builtin.set_fact:
        ffmpeg_arch: "{{ ansible_architecture }}"
```


do later

```bash
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows```

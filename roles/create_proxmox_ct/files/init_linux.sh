#!/usr/bin/env bash

# Setup a VM for ansible
# curl --silent https://raw.githubusercontent.com/kism/ansible-playbooks/main/roles/create_proxmox_ct/files/init_linux.sh | bash

# All users and groups defined in https://github.com/kism/ansible-playbooks/blob/main/roles/configure_users/vars/main.yml
# This script onboards the a user manually for onboarding
account="ansible_svc"
account_uid=1088
group="kgadmins"
group_gid=1099

packages="curl tar sudo acl python3 openssh-server"
dnf --setopt=install_weak_deps=False --best install -y $packages || apk add $packages || apt-get --no-install-recommends -y install $packages || pacman -S --noconfirm $packages || pkg install $packages

id -u $account &>/dev/null || useradd --uid $account_uid $account
groupadd --gid $group_gid $group
usermod -a -G $group $account
usermod -p '*' $account
chage -I -1 -m 0 -M 99999 -E -1 $account
mkdir -p /home/$account/.ssh
echo "%$group ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/$group
chmod 440 /etc/sudoers.d/$group
curl -s https://github.com/kism.keys > /home/$account/.ssh/authorized_keys
chown -R $account:$account /home/$account
chmod 700 /home/$account/.ssh
chmod 600 /home/$account/.ssh/authorized_keys

# Enable and start ssh server
if [ -h /etc/systemd/system/sshd.service ]; then
    systemctl enable ssh.service
    systemctl start ssh.service
else
    systemctl enable sshd.service
    systemctl start sshd.service
fi

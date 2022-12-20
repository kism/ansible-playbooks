# curl --silent https://raw.githubusercontent.com/kism/ansible-playbooks/master/onboard/init.sh | bash
packages="curl tar sudo acl"
dnf --setopt=install_weak_deps=False --best install -y $packages || apk add $packages || apt-get --no-install-recommends -y install $packages || pacman -S --noconfirm $packages || pkg install $packages

publickeys="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKCzVh8CktGh+5LlZJfeBj/VcRzGO6zjrW2p2dM+X4PA ansible_svc\nssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIDLGih8ZZL9fwTCiKKmlyrHJXVQvKENZQMf2+/G8z65 root@DPSHUB"
account="ansible_svc"
group="kgadmins"

id -u $account &>/dev/null || useradd $account
groupadd $group
usermod -a -G $group $account
usermod -p '*' $account
chage -I -1 -m 0 -M 99999 -E -1 $account
mkdir -p /home/$account/.ssh
echo "%$group ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/$group
echo -e $publickeys > /home/$account/.ssh/authorized_keys
chown -R $account:$account /home/$account
chmod 700 /home/$account/.ssh
chmod 600 /home/$account/.ssh/authorized_keys

publickey="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKCzVh8CktGh+5LlZJfeBj/VcRzGO6zjrW2p2dM+X4PA ansible_svc"
account="ansible_svc"

id -u $account &>/dev/null || useradd $account
usermod -a -G wheel $account &>/dev/null || usermod -a -G sudo $account
mkdir -p /home/$account/.ssh
echo "$account ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/$account
echo $publickey > /home/$account/.ssh/authorized_keys
chown -R $account:$account /home/$account
chmod 700 /home/$account/.ssh
chmod 600 /home/$account/.ssh/authorized_keys

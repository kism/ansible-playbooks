publickey="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKCzVh8CktGh+5LlZJfeBj/VcRzGO6zjrW2p2dM+X4PA ansible_svc"
id -u somename &>/dev/null || useradd ansible_svc
usermod -a -G wheel ansible_svc || usermod -a -G sudo ansible_svc
mkdir -p /home/ansible_svc/.ssh
echo $publickey > /home/ansible_svc/.ssh/authorized_keys
chown -R ansible_svc:ansible_svc /home/ansible_svc
chmod 700 /home/ansible_svc/.ssh
chmod 600 /home/ansible_svc/.ssh/authorized_keys

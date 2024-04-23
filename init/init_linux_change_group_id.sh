#!/usr/bin/env bash

# This script is used specifically changing UIDs of users,
# All users and groups defined in https://github.com/kism/ansible-playbooks/blob/main/roles/configure_users/vars/main.yml

user=ansible_svc
user_olduid=1000
user_newuid=1088

echo $user
echo $user_olduid
echo $user_newuid

usermod -u $user_newuid $user
groupmod -g $user_newuid $user

declare -a folders=("home" "srv" "opt" "etc" "media" "mnt")

find /srv -user  $user_olduid -exec chown  -h $user {} \;
find /srv -group $user_olduid -exec chgrp -h $user {} \;

find /home -user  $user_olduid -exec chown  -h $user {} \;
find /home -group $user_olduid -exec chgrp -h $user {} \;


#!/usr/bin/env bash

# This script is used specifically changing UIDs of users,
# All users and groups defined in https://github.com/kism/ansible-playbooks/blob/main/roles/configure_users/vars/main.yml

group=kgadmins
group_olduid=1099
group_newuid=1099

echo $group
echo $group_olduid
echo $group_newuid

groupmod -g $group_newuid $group

declare -a folders=("home" "srv" "opt" "etc" "media" "mnt")

find /srv -group $group_olduid -exec chgrp -h $group {} \;

find /home -group $group_olduid -exec chgrp -h $group {} \;

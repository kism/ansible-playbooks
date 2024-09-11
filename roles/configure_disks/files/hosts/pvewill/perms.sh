#! /usr/bin/env bash

set -e

partition_list=(Quina Marcus Blank Beatrix Steiner)

echo -- /srv

echo - Remove ACLs

for partition in "${partition_list[@]}"; do
    setfacl --remove-all --recursive /srv/$partition
done

echo - Access for parition mount folders
# no group write to prevent files getting created directly in them
chown root:root /srv
chmod u=rwX,g=rX,o=rX /srv
chmod g-s /srv
chmod g-s /srv/*

for partition in "${partition_list[@]}"; do
    chmod u=rwX,g=rX,o=rX /srv/$partition
done

echo - Set Owners
for partition in "${partition_list[@]}"; do
    chown root:root /srv/$partition
done

echo -- Subfolders

echo - Set ACLs

sudo setfacl -d -R -m u::rwX,g::rwX,o::0 /srv/Quina/z
sudo setfacl -d -R -m u::rwX,g::rwX,o::0 /srv/Quina/downloads

echo - Set Permissions

chown -R kism:content_private /srv/Quina/z
chown -R qbtuser:qbtuser /srv/Quina/downloads

chown -R root:root /srv/Marcus
chown -R root:root /srv/Blank
chown -R root:root /srv/Beatrix
chown -R root:root /srv/Steiner

echo -- Finds

echo - Find all dirs, set setguid

for partition in "${partition_list[@]}"; do
    find /srv/$partition -mindepth 1 -type d -exec chmod g+s {} +
done

echo - Find all files, remove all special bits

for partition in "${partition_list[@]}"; do
    find /srv/$partition -type f -exec chmod u-s,g-s,o-s {} +
done

echo - Recursively set perms on subfolders of all content mounts

for partition in "${partition_list[@]}"; do
    find /srv/$partition -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
done

echo -- Fun file exceptions
chown root:root /srv/*/lost+found
chmod 0700 /srv/*/lost+found
chmod g-s /srv/*/lost+found # huh

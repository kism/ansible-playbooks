#! /usr/bin/env bash

set -e

partition_list=(Amarant Freya Garnet Vivi Eiko Zidane)

content_partition_list=(Amarant Freya Garnet Vivi)
parity_partition_list=(Eiko Zidane)

# region /srv
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

for partition in "${content_partition_list[@]}"; do
    chmod u=rwX,g=rX,o=rX /srv/$partition
done

for partition in "${parity_partition_list[@]}"; do
    chmod u=rwX,g=,o= /srv/$partition
done

echo - Set Owners

for partition in "${partition_list[@]}"; do
    chown root:root /srv/$partition
done

# endregion

# region Subfolders
echo -- Subfolders

echo - Set ACLs

for partition in "${content_partition_list[@]}"; do
    sudo setfacl -d -R -m u::rwX,g::rwX,o::0 /srv/$partition
done

echo - Set Permissions

echo - Set Permissions for Content
chown -R backup_svc:backup_svc /srv/Amarant/backups
chown -R kism:content_private /srv/Amarant/Downloads
chown -R kism:content_private /srv/Amarant/Temp
chown -R kism:content_public /srv/Amarant/Video

chown -R kism:content_public /srv/Freya/Apps
chown -R kism:content_public /srv/Freya/Emulators
chown -R kism:content_public /srv/Freya/Fonts
chown -R kism:content_public /srv/Freya/ROMs
chown -R kism:content_public /srv/Freya/Video
chown -R kism:content_public /srv/Freya/videoscratch

chown -R kism:content_public /srv/Garnet/Download
chown -R kism:content_public /srv/Garnet/eBooks
chown -R kism:content_public /srv/Garnet/Fonts
chown -R kism:content_public /srv/Garnet/ROMs
chown -R kism:content_public /srv/Garnet/Video

chown -R kism:content_public /srv/Vivi/Music
chown -R kism:content_private /srv/Vivi/Pictures
chown -R kism:content_public /srv/Vivi/ps2smb
chown -R kism:content_public /srv/Vivi/Video

# endregion

# region Finds
echo -- Finds

echo - Find all dirs, set setguid

for partition in "${content_partition_list[@]}"; do
    find /srv/$partition -mindepth 1 -type d -exec chmod g+s {} +
done

echo - Find all files, remove all special bits

for partition in "${content_partition_list[@]}"; do
    find /srv/$partition -type f -exec chmod u-s,g-s,o-s {} +
done

echo - Recursively set perms on subfolders of all content mounts

for partition in "${content_partition_list[@]}"; do
    find /srv/$partition -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
done

# endregion

# region Exceptions
echo -- Fun file exceptions

chown root:root /srv/*/snapraid*
chown 0600 /srv/*/snapraid*

set +e
chown root:root /srv/*/lost+found
chmod 0700 /srv/*/lost+found
chmod g-s /srv/*/lost+found # huh
# endregion

echo done!

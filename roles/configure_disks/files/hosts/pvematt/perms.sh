#! /usr/bin/env bash

echo -- /srv

echo - Remove ACLs
setfacl --remove-all --recursive /srv/Amarant
setfacl --remove-all --recursive /srv/Freya
setfacl --remove-all --recursive /srv/Garnet
setfacl --remove-all --recursive /srv/Vivi
setfacl --remove-all --recursive /srv/Eiko
setfacl --remove-all --recursive /srv/Zidane

echo - Let everyone get to the hard drive partitions,
echo   no group write to prevent files getting created directly in them
chown root:root /srv
chmod u=rwX,g=rX,o=rX /srv
chmod g-s /srv
chmod g-s /srv/*
chmod u=rwX,g=rX,o=rX /srv/Amarant
chmod u=rwX,g=rX,o=rX /srv/Freya
chmod u=rwX,g=rX,o=rX /srv/Garnet
chmod u=rwX,g=rX,o=rX /srv/Vivi
chmod u=rwX,g=,o= /srv/Eiko # only touched by snapraid
chmod u=rwX,g=,o= /srv/Zidane # only touched by snapraid

echo - Set Owners
chown root:root /srv/Amarant
chown root:root /srv/Freya
chown root:root /srv/Garnet
chown root:root /srv/Vivi
chown root:root /srv/Eiko # only touched by snapraid
chown root:root /srv/Zidane # only touched by snapraid

echo -- Subfolders

echo - Set Permissions for Content
chown -R backup_svc:backup_svc /srv/Amarant/backups
chown -R kism:content_private  /srv/Amarant/Downloads
chown -R kism:content_private  /srv/Amarant/Temp
chown -R kism:content_public   /srv/Freya/Video

chown -R kism:content_public  /srv/Freya/Apps
chown -R kism:content_public  /srv/Freya/Emulators
chown -R kism:content_public  /srv/Freya/Fonts
chown -R kism:content_public  /srv/Freya/ROMs
chown -R kism:content_public  /srv/Freya/Video
chown -R kism:content_public  /srv/Freya/videoscratch

chown -R kism:content_public  /srv/Garnet/Download
chown -R kism:content_public  /srv/Garnet/eBooks
chown -R kism:content_public  /srv/Garnet/Fonts
chown -R kism:content_public  /srv/Garnet/ROMs
chown -R kism:content_public  /srv/Garnet/Video

chown -R kism:content_public  /srv/Vivi/Music
chown -R kism:content_private /srv/Vivi/Pictures
chown -R kism:content_public  /srv/Vivi/ps2smb
chown -R kism:content_public  /srv/Vivi/Video

echo -- Finds

echo - Find all dirs, set setguid
find /srv/Amarant -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Freya   -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Garnet  -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Vivi    -mindepth 1 -type d -exec chmod g+s {} +

echo - Find all files, remove all special bits
find /srv/Amarant -type f -exec chmod u-s,g-s,o-s {} +
find /srv/Freya   -type f -exec chmod u-s,g-s,o-s {} +
find /srv/Garnet  -type f -exec chmod u-s,g-s,o-s {} +
find /srv/Vivi    -type f -exec chmod u-s,g-s,o-s {} +

echo - Recursively set perms on subfolders of all content mounts
find /srv/Amarant -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
find /srv/Freya   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
find /srv/Garnet  -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
find /srv/Vivi    -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +

echo -- Fun file exceptions
chown root:root /srv/*/lost+found
chmod 0700 /srv/*/lost+found
chmod g-s /srv/*/lost+found # huh
chown root:root /srv/*/snapraid*
chown 0600 /srv/*/snapraid*

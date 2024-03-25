# /srv

## Remove ACLs
setfacl --remove-all --recursive /srv/Amarant
setfacl --remove-all --recursive /srv/Freya
setfacl --remove-all --recursive /srv/Garnet
setfacl --remove-all --recursive /srv/Vivi
setfacl --remove-all --recursive /srv/Eiko
setfacl --remove-all --recursive /srv/Zidane

## Let everyone get to the hard drive partitions
chown root:root /srv
chmod u=rwX,g=rX,o=rX /srv
chmod g-s /srv
chmod g-s /srv/*
chmod u=rwX,g=rX,o=rX /srv/Amarant
chmod u=rwX,g=rX,o=rX /srv/Freya
chmod u=rwX,g=rX,o=rX /srv/Garnet
chmod u=rwX,g=rX,o=rX /srv/Vivi
chmod u=rwX,g=rX,o=rX /srv/Eiko # only touched by snapraid
chmod u=rwX,g=rX,o=rX /srv/Zidane # only touched by snapraid

## Set Owners
chown kism:content_public /srv/Amarant
chown kism:content_public /srv/Freya
chown kism:content_public /srv/Garnet
chown kism:content_public /srv/Vivi
chown root:root /srv/Eiko # only touched by snapraid
chown root:root /srv/Zidane # only touched by snapraid

# Subfolders

## Set Permissions for Content
chown -R backup_svc:backup_svc /srv/Amarant/backups
chown -R kism:content_private  /srv/Amarant/Downloads
chown -R kism:content_private  /srv/Amarant/Temp

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

## Set setgid to directories recursively
find /srv/Amarant -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Freya   -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Garnet  -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Vivi    -mindepth 1 -type d -exec chmod g+s {} +

## Recursively set perms on subfolders of all content mounts
find /srv/Amarant -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /srv/Freya   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /srv/Garnet  -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /srv/Vivi    -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +

# Misc

## Fun file exceptions
chown root:root /srv/*/lost+found
chmod 0700 /srv/*/lost+found
chmod g-s /srv/*/lost+found # huh
chown root:root /srv/*/snapraid*
chown 0600 /srv/*/snapraid*

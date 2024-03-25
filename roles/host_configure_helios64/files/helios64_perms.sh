# /srv

## Remove ACLs
setfacl --remove-all --recursive /srv/Quina
setfacl --remove-all --recursive /srv/Quale
setfacl --remove-all --recursive /srv/Steiner

## Let everyone get to the hard drive partitions
chown root:root /srv
chmod u=rwX,g=rX,o=rX /srv
chmod g-s /srv
chmod g-s /srv/*
chmod u=rwX,g=rX,o=rX /srv/Quina
chmod u=rwX,g=rX,o=rX /srv/Quale
chmod u=rwX,g=rX,o=rX /srv/Steiner

## Set Owners
chown kism:content_public /srv/Quina
chown kism:content_public /srv/Quale
chown kism:content_public /srv/Steiner

# Subfolders

## Set Permissions for Content
chown -R kism:content_private /srv/Quina/z
chown -R qbtuser:qbtuser /srv/Quina/downloads
chown -R kism:content_private /srv/Quina/configs

## Set setgid to directories recursively
find /srv/Quina   -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Quale   -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Steiner -mindepth 1 -type d -exec chmod g+s {} +

## Recursively set perms on subfolders of all content mounts
find /srv/Quina   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /srv/Quale   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /srv/Steiner -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +

# Misc

## Fun file exceptions
chown root:root /srv/*/lost+found
chmod 0700 /srv/*/lost+found
chmod g-s /srv/*/lost+found # huh
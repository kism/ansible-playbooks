# /mnt

## Remove ACLs
setfacl --remove-all --recursive /mnt/Quina
setfacl --remove-all --recursive /mnt/Quale
setfacl --remove-all --recursive /mnt/Steiner

## Let everyone get to the hard drive partitions
chown root:root /mnt
chmod u=rwX,g=rX,o=rX /mnt
chmod g-s /mnt
chmod g-s /mnt/*
chmod u=rwX,g=rX,o=rX /mnt/Quina
chmod u=rwX,g=rX,o=rX /mnt/Quale
chmod u=rwX,g=rX,o=rX /mnt/Steiner

## Set Owners
chown kism:content_public /mnt/Quina
chown kism:content_public /mnt/Quale
chown kism:content_public /mnt/Steiner

# Subfolders

## Set Permissions for Content
chown -R kism:content_private /mnt/Quina/z
chown -R qbtuser:qbtuser /mnt/Quina/downloads
chown -R kism:content_private /mnt/Quina/configs

## Set setgid to directories recursively
find /mnt/Quina   -mindepth 1 -type d -exec chmod g+s {} +
find /mnt/Quale   -mindepth 1 -type d -exec chmod g+s {} +
find /mnt/Steiner -mindepth 1 -type d -exec chmod g+s {} +

## Recursively set perms on subfolders of all content mounts
find /mnt/Quina   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /mnt/Quale   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +
find /mnt/Steiner -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rX,o-wrx {} +

# Misc

## Fun file exceptions
chown root:root /mnt/*/lost+found
chmod 0700 /mnt/*/lost+found
chmod g-s /mnt/*/lost+found # huh
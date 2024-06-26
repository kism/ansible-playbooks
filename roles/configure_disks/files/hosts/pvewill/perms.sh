#! /usr/bin/env bash

echo -- /srv

echo - Remove ACLs
setfacl --remove-all --recursive /srv/Quina
setfacl --remove-all --recursive /srv/Quale
setfacl --remove-all --recursive /srv/Steiner

echo - Let everyone get to the hard drive partitions,
echo   no group write to prevent files getting created directly in them
chown root:root /srv
chmod u=rwX,g=rX,o=rX /srv
chmod g-s /srv
chmod g-s /srv/*
chmod u=rwX,g=rX,o=rX /srv/Quina
chmod u=rwX,g=rX,o=rX /srv/Quale
chmod u=rwX,g=rX,o=rX /srv/Steiner

echo - Set Owners
chown root:root /srv/Quina
chown root:root /srv/Quale
chown root:root /srv/Steiner

echo -- Subfolders

echo - Set Permissions for Content
chown -R kism:content_private /srv/Quina/z
chown -R qbtuser:qbtuser /srv/Quina/downloads
chown -R qbtuser:qbtuser /srv/Quina/configs

echo -- Finds

echo - Find all dirs, set setguidfind
find /srv/Quina    -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Quale    -mindepth 1 -type d -exec chmod g+s {} +
find /srv/Steiner  -mindepth 1 -type d -exec chmod g+s {} +

echo - Find all files, remove all special bits
find /srv/Quina   -type f -exec chmod u-s,g-s,o-s {} +
find /srv/Quale   -type f -exec chmod u-s,g-s,o-s {} +
find /srv/Steiner -type f -exec chmod u-s,g-s,o-s {} +

echo - Recursively set perms on subfolders of all content mounts
find /srv/Quina   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
find /srv/Quale   -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +
find /srv/Steiner -mindepth 1 -maxdepth 1 -type d -exec chmod -R u=rwX,g+rwX,o= {} +

echo -- Fun file exceptions
chown root:root /srv/*/lost+found
chmod 0700 /srv/*/lost+found
chmod g-s /srv/*/lost+found # huh
# Set Permissions for Content
chown -R kism:content_private  /srv/Amarant/Downloads
chown -R kism:content_private  /srv/Amarant/Temp
chown -R backup_svc:backup_svc /srv/Amarant/backups

chown -R kism:content_public  /srv/Freya/Apps
chown -R kism:content_public  /srv/Freya/Emulators
chown -R kism:content_public  /srv/Freya/Fonts
chown -R kism:content_public  /srv/Freya/ROMs
chown -R kism:content_public  /srv/Freya/Video
chown -R kism:content_private /srv/Freya/z

chown -R kism:content_public  /srv/Garnet/Download
chown -R kism:content_public  /srv/Garnet/eBooks
chown -R kism:content_public  /srv/Garnet/Fonts
chown -R kism:content_public  /srv/Garnet/ROMs
chown -R kism:content_public  /srv/Garnet/Video
chown -R kism:content_private /srv/Garnet/z

chown -R kism:content_public  /srv/Vivi/Music
chown -R kism:content_private /srv/Vivi/Pictures
chown -R kism:content_public  /srv/Vivi/ps2smb
chown -R kism:content_public  /srv/Vivi/Video

chown kism:content_public /srv/Amarant
chown kism:content_public /srv/Freya
chown kism:content_public /srv/Garnet
chown kism:content_public /srv/Vivi

# These are only touched by snapraid
chown root:root /srv/Eiko
chown root:root /srv/Zidane

# Fix Dirs
chmod -R o-wrx,g+rX,u=+rwX /srv/Garnet
chmod -R o-wrx,g+rX,u=+rwX /srv/Amarant
chmod -R o-wrx,g+rX,u=+rwX /srv/Freya
chmod -R o-wrx,g+rX,u=+rwX /srv/Vivi

# Let everyone get to the hard drive partitions
chmod o+rX,g+rX,u=+rX /srv
chmod o+rX,g+rX,u=+rX /srv/Garnet
chmod o+rX,g+rX,u=+rX /srv/Amarant
chmod o+rX,g+rX,u=+rX /srv/Freya
chmod o+rX,g+rX,u=+rX /srv/Vivi
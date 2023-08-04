cp /etc/letsencrypt/live/HOSTNAME/fullchain.pem /etc/pve/local/pveproxy-ssl.pem
cp /etc/letsencrypt/live/HOSTNAME/privkey.pem /etc/pve/local/pveproxy-ssl.key
systemctl reload pveproxy
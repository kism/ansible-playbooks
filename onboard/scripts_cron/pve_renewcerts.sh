cp /etc/letsencrypt/live/pve.kg.lan/fullchain.pem /etc/pve/local/pveproxy-ssl.pem
cp /etc/letsencrypt/live/pve.kg.lan/privkey.pem /etc/pve/local/pveproxy-ssl.key
systemctl reload pveproxy
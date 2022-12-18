#!/usr/bin/env bash

PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/sbin:/usr/local/bin

sleep $(shuf -i 0-1000 -n 1)

REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/kglan_root.cer \
    certbot certonly                                 \
    --agree-tos --email=kg@localhost                 \
    -v -n --nginx                                    \
    -d graf.kg.lan                                   \
    --server https://cert.kg.lan/acme/acme/directory
	
systemctl reload nginx




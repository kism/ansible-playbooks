#!/usr/bin/env bash

set -e

python3 -c 'import random; import time; time.sleep(random.random() * 3600)'

/usr/bin/certbot renew -q

cp /etc/letsencrypt/live/kierangee.au/* /etc/elasticsearch/certs/

chown -R root:elasticsearch /etc/elasticsearch/certs/*

chmod 640 /etc/elasticsearch/certs/*

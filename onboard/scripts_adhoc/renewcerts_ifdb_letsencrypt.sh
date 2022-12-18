#!/usr/bin/env bash

PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/sbin:/usr/local/bin

sleep $(shuf -i 0-1000 -n 1)

certbot certonly                            \
    --agree-tos                             \
    --email=kieran.lost.the.game@gmail.com  \
    -v -n --standalone                      \
    -d kism.duckdns.org

chown influxdb:influxdb /etc/letsencrypt/archive/kism.duckdns.org/*

systemctl reload influxdb


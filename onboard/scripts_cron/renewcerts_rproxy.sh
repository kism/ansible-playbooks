#!/usr/bin/env bash

PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/sbin:/usr/local/bin

sleep $(shuf -i 0-1000 -n 1)

certbot                                  \
--agree-tos --email=geekieran@gmail.com          \
-v -n --nginx                                    \
-d kierangee.au                                  \
-d influxdb2.kierangee.au                        \
-d flaskcontroller.kierangee.au

systemctl reload nginx




#!/usr/bin/env bash
openssl s_client -showcerts -connect localhost:8006 </dev/null 2>/dev/null | openssl x509 -outform PEM > /etc/ssl/certs/pveproxy-fetched.cer

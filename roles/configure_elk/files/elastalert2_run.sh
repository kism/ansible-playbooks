#!/bin/sh
set -e
~/.local/bin/elastalert-create-index --config /opt/elastalert2/config.yml
~/.local/bin/elastalert --config /opt/elastalert2/config.yml

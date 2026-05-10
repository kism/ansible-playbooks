#! /usr/bin/env bash

partition_list=(kism-bak-1 kism-bak-2 kism-bak-3)

for partition in "${partition_list[@]}"; do
    chown root:root /srv/$partition
    chmod u=rwX,g=,o= /srv/$partition
done

for partition in "${partition_list[@]}"; do
    chown -R kism:content_private /srv/"$partition"/*
    chmod -R u=rwX,g=rX,o= /srv/"$partition"/*
done

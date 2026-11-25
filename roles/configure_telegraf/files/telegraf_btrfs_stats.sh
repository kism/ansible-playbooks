#!/bin/sh
# btrfs device error counters as influx line protocol, telegraf has no btrfs input.
# btrfs_device,mount=/srv/Blank,device=/dev/sdc1 write_io_errs=0i,read_io_errs=2927i,...
# The counters only ever grow (until btrfs device stats -z), alert on any increase
for mount in $(findmnt -t btrfs -nro TARGET); do
    sudo -n /usr/bin/btrfs device stats "$mount" | awk -v mount="$mount" '
        # [/dev/sdc1].read_io_errs    2927
        {
            split($1, part, "]."); device = substr(part[1], 2)
            fields[device] = fields[device] (fields[device] ? "," : "") part[2] "=" $2 "i"
        }
        END { for (device in fields) print "btrfs_device,mount=" mount ",device=" device " " fields[device] }'
done

#!/bin/bash
# Run by btrfs-scrub.service (btrfs-scrub-no-abort.conf drop-in) instead of btrfsmaintenance's btrfs-scrub.sh,
# which exits at the first filesystem with errors so the ones after it never get scrubbed.
# Scrubs every btrfs mount and exits 1 if any had errors.
# ponytail: a filesystem mounted twice (subvol mounts) gets scrubbed twice, dedupe by UUID if that ever happens

# A <3>/<4> line prefix sets the journal priority (systemd SyslogLevelPrefix), so ERROR/WARNING lines get a level
exec > >(sed -u -e '/ERROR/s/^/<3>/' -e '/WARNING/s/^/<4>/') 2>&1

rc=0
for mount in $(findmnt -t btrfs -nro TARGET); do
    echo "Running scrub on $mount"
    if ! btrfs scrub start -Bd "$mount"; then
        echo "ERROR: scrub of $mount found errors or failed"
        rc=1
    fi
done
exit $rc

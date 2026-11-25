# Todo

- Figure out ssd biggest users

## Bugs found in the 2026-11-24 role audit

The rest were fixed on 2026-11-24.

- `roles/configure_rsync_backup_target/tasks/main.yml:5`: `backup_svc ALL=(ALL) NOPASSWD: /usr/bin/btrfs` is effectively root. Narrow it to the subcommands the backup uses. Needs the backup script on the source machine (not in this repo) to see which `btrfs` subcommands it runs.

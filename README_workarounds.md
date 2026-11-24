# Known workarounds

Things that work around someone else's bug or limitation. Check each one now and then, and remove the workaround once it's no longer needed.

"(inferred)" means no comment in the code states the reason; it was worked out from what the code does. Line numbers are as of 2026-11-24.

## configure_concept_sd_rootfs

- **journald `SystemMaxUse=5M`** (`roles/configure_concept_sd_rootfs/tasks/main.yml:5`)
  - Why: the task says "20M seems to break". The cause isn't recorded; SD card or rootfs size is likely. It also edits the vendor `journald.conf` directly instead of using a `journald.conf.d` drop-in.
  - Check: try 20M on a test SD host and watch `journalctl --disk-usage` and the boot logs.

## configure_disks / configure_docker

- **duperemove built from source in Docker** (`roles/configure_disks/files/duperemove/Dockerfile:1`)
  - Why: Debian only packages 0.11. The build skips `make install` because that needs pandoc.
  - Check: `apt-cache policy duperemove`. At 0.15 or later, drop the build. Last checked 2026-11-24: trixie and trixie-backports have 0.11.2, sid has 0.15.2 (same as the build). Drop the build once it reaches trixie-backports, or with Debian 14.
- **duperemove and lazydocker symlinked into `/usr/bin`** (`roles/configure_disks/tasks/02-duperemove.yml:44`, `roles/configure_docker/tasks/02-lazydocker.yml:26`)
  - Why: on Oracle Linux, sudo's `secure_path` and root's login PATH skip `/usr/local/bin`.
  - Check: `sudo grep secure_path /etc/sudoers` and `sudo -i sh -c 'echo $PATH'` on an OL host. Last checked 2026-11-24: still `/sbin:/bin:/usr/sbin:/usr/bin` on every OL host, and root's login PATH lacks `/usr/local/bin` on most.

## configure_docker_arr

- **seerr config chowned to uid 1000** (`roles/configure_docker_arr/tasks/main.yml:24`)
  - Why: the seerr image runs as `node` (uid 1000) and ignores PUID/PGID, unlike the linuxserver images.
  - Check: the seerr image docs for PUID support, or `docker exec seerr id`. Last checked 2026-11-24: still `USER node:node` with Node's stock `docker-entrypoint.sh`, no PUID handling. A compose `user:` could match the other arr containers instead, but that's a re-chown either way.

## configure_docker_qbittorrent

- **`Restart=on-failure` on a oneshot compose unit** (`roles/configure_docker_qbittorrent/templates/docker-qbittorrent.service.j2:14`)
  - Why (inferred): at boot `compose up` can fail while gluetun isn't healthy yet (`depends_on: condition: service_healthy`), so the unit retries.
  - Check: `journalctl -u docker-qbittorrent -b` for failed first attempts. Last checked 2026-11-24: still needed. On yoho (2026-11-18) gluetun stayed unhealthy past the old 3 tries in about 90s and the unit was left `failed`, so it now retries every 60s with no start limit.

## configure_docker_victoriametrics

- **vmauth legacy paths for bigbilly** (`legacy_paths: true` on its token in `inventory/host_vars/vic.yml`, the journal user's old route in `templates/auth.yml.j2`, rproxy `vic.conf`, added 2026-11-24)
  - Why: everything moved to `/metrics`, `/logs` and `/firewall`, but bigbilly was unreachable and still posts to the old root and `/insert/journald/` paths.
  - Check: once bigbilly is reachable, run `configure_telegraf.yml` and `configure_journal_upload.yml` on it. Then remove `legacy_paths: true`, the journal user's `ponytail: legacy` route, and the old `/insert/journald/` location in `vic.conf`.
- **Daily SIGHUP to vector for GeoIP** (`roles/configure_docker_victoriametrics/files/vector-geoip-reload.timer`, added 2026-11-24)
  - Why: vector only reads the mmdb at startup or on SIGHUP. Replacing the file alone does nothing (tested 2026-11-24 on 0.62).
  - Check: the vector changelog for automatic `enrichment_tables` file reloads. Retest by swapping the mmdb and querying a known IP.
- **Vector Elasticsearch sink healthchecks disabled** (`roles/configure_docker_victoriametrics/files/vector.yaml:107`)
  - Why: VictoriaLogs' Elasticsearch-compatible endpoint doesn't answer what vector's ES healthcheck probes. The VictoriaLogs docs recommend this setting.
  - Check: set it to `enabled: true` and look for healthcheck errors in `docker logs vector`. Last checked 2026-11-24 (vector 0.62, victoria-logs latest): still `Healthcheck failed ... 400 Bad Request`, data flows regardless.
- **Vector image pinned** (`roles/configure_docker_victoriametrics/files/docker-compose.yml:42`)
  - Why: VRL can break across releases. This is a precaution, not a known bad version.
  - Check: bump it, then `docker exec vector vector test /etc/vector/vector.yaml`. Last checked 2026-11-24: the pin (0.62.0) is the latest release.
- **`_MACHINE_ID` left out of the journald stream fields** (`roles/configure_docker_victoriametrics/files/docker-compose.yml:24`)
  - Why: Proxmox doesn't regenerate `/etc/machine-id` when a container is cloned, so cloned CTs share it.
  - Check: compare `cat /etc/machine-id` across the LXC hosts. If every value is unique, the field could go back in. Last checked 2026-11-24: all 15 reachable hosts unique, but the next clone would reintroduce a dupe, so it stays out.

## configure_headscale

- **headscale logs JSON** (`roles/configure_headscale/files/config.yaml:286`, plus the in-place replace in `tasks/main.yml` because `config.yaml` is copied with `force: false`)
  - Why: Docker's journald driver marks all stderr as PRIORITY=3, so every headscale line looked like an error. Grafana reads the real `level` from the JSON.
  - Check: Docker's journald driver gaining per-line priority, or headscale logging to stdout.
- **headplane healthcheck every 5m** (`roles/configure_headscale/files/docker-compose.yml:36`)
  - Why: the image's healthcheck polls headscale `/health`, and headscale logs every poll at INF (about 2.9k lines/day at the default 30s).
  - Check: `docker inspect ghcr.io/tale/headplane:latest --format '{{json .Config.Healthcheck}}'`, or headscale no longer logging `/health`. Last checked 2026-11-24: image still defaults to 30s, and headscale v0.29.7 still logs each `/health` poll as an info `http request` line.

## configure_jumpbox

- **curl User-Agent in the motd script** (`roles/configure_jumpbox/files/motd.py:12`)
  - Why: Cloudflare bot protection blocks Python-urllib's default User-Agent.
  - Check: run the same request without the header. A 403 or error 1010 means it's still needed. Last checked 2026-11-24: Python's default UA still gets 403 `error code: 1010`. It's your own zone, so a Cloudflare WAF skip rule for that API path would also fix it.

## configure_locale

- **Ghostty terminfo compiled with `tic`** (`roles/configure_locale/tasks/main.yml:35`)
  - Why: the distros' terminfo doesn't include `xterm-ghostty`, which is the TERM Ghostty sets by default.
  - Check: `infocmp xterm-ghostty` on a fresh target. Last checked 2026-11-24: Debian 13 (ncurses 6.5) and Arch (6.6) ship the entry, but named `ghostty`, not `xterm-ghostty`. OL9 (6.2) and OL10 (6.4) have neither. Still needed while OL hosts exist, or until ncurses adds the `xterm-ghostty` alias.

## configure_manjaro_laptop

- **Toshy installer fed `y` on stdin** (`roles/configure_manjaro_laptop/tasks/02-toshy.yml:36`)
  - Why: `setup_toshy.py` asks about the KWin switcher interactively.
  - Check: `./setup_toshy.py install --help` at the pinned ref, for a flag that answers it. Last checked 2026-11-24 (pinned v26.08.0 and `main`): `check_kde_app_switcher()` still calls `input()` with no flag. It's skipped once `~/.local/share/kwin/scripts/applicationswitcher` exists.
- **KDE wallpaper set through a D-Bus JS snippet** (`roles/configure_manjaro_laptop/tasks/04-kde-wallpaper.yml:25`)
  - Why: the colour wallpaper plugin has no CLI equivalent of `plasma-apply-wallpaperimage`.
  - Check: Plasma release notes, or `plasma-apply-wallpaperimage --help`. Last checked 2026-11-24 (plasma-workspace `master`): its only option is `-f/--fill-mode` and it takes an image, so there's still no CLI for the colour plugin.

## configure_mergerfs

- **`KillMode=none` plus a pre-start umount** (`roles/configure_mergerfs/templates/mergerfs.service.j2:7`)
  - Why (inferred): a crashed FUSE process leaves a dead mount ("Transport endpoint is not connected"). `KillMode=none` is from mergerfs's example unit; systemd has deprecated it and warns.
  - Check: `journalctl -u mergerfs | grep -i KillMode`, and mergerfs's current example unit. Last checked 2026-11-24: upstream's quickstart unit (`mkdocs/docs/quickstart.md`) still uses `KillMode=none`, the same as ours apart from the pre-start umount. bigbilly was unreachable, so the journal wasn't checked.

## configure_misc

- **NetworkManager IPv6 warnings silenced** (`roles/configure_misc/tasks/main.yml:114`, `/etc/NetworkManager/conf.d/99-quiet-ip6.conf`, added 2026-11-24)
  - Why: libndp sends router solicitations with `sa_family=AF_UNSPEC`, and the PVE 7.0 kernel rejects that. NM logs `failure sending router solicitation: Address family not supported by protocol (97)` about every minute. Harmless, because RAs still arrive unsolicited.
  - Check: on one host, `nmcli general logging domains DEFAULT` then `journalctl -u NetworkManager -f | grep solicit` for a few minutes. Quiet = fixed, delete the task and the file. Last checked 2026-11-24 on vic: 2 errors in 3 minutes, still needed.
- **`sys-kernel-config.mount` and `sys-kernel-debug.mount` masked in LXC** (`roles/configure_misc/tasks/main.yml:33`)
  - Why: unprivileged containers can't mount configfs or debugfs, so the units fail.
  - Check: in one container, unmask them and `systemctl start sys-kernel-debug.mount`, then `systemctl --failed`. Last checked 2026-11-24 on code (OL, PVE 9): both still fail.
- **`follow: true` on `/etc/vconsole.conf`** (`roles/configure_misc/tasks/main.yml:40`)
  - Why: Debian symlinks it to `/etc/default/keyboard`, which may not exist.
  - Check: `readlink -f /etc/vconsole.conf` on Debian 13. Last checked 2026-11-24 (debian:13 container): still there. systemd's `/usr/lib/tmpfiles.d/debian.conf` creates `L+ /etc/vconsole.conf -> default/keyboard`, which dangles until `keyboard-configuration` is installed.

## configure_motd

- **sed strips the ESM adverts** (`roles/configure_motd/files/update-motd/50-sysinfo:29`)
  - Why (inferred): Ubuntu Pro adverts appear in `/var/lib/update-notifier/updates-available`.
  - Check: `cat` that file on a current Ubuntu host. No host runs Ubuntu as of 2026-11-24, so this code never runs; `$stamp` only exists on Ubuntu.

## configure_nginx

- **Distro nginx packages removed on EL** (`roles/configure_nginx/tasks/01-redhat.yml:44`, "bit of a hack")
  - Why: AppStream's split nginx packages (`nginx-core`, modules) conflict with nginx.org's single package.
  - Check: `rpm -qa 'nginx*' --qf '%{NAME} %{RELEASE}\n' | grep -v ngx` on EL hosts. Last checked 2026-11-24 (oraclelinux:9 container): still needed. nginx.org's package has no `Obsoletes`, and installing it over AppStream nginx fails on `nginx-core` file conflicts (`/etc/logrotate.d/nginx`, `/etc/nginx/mime.types`). rproxy has no distro nginx left, only `nginx-filesystem`, which doesn't conflict.
- **`module_hotfixes: true` on the nginx.org repo** (`roles/configure_nginx/tasks/01-redhat.yml:28`)
  - Why (inferred, nginx.org's documented advice): stops dnf modularity hiding nginx.org packages behind the AppStream module. EL10 dropped modularity.
  - Check: `dnf module list nginx`. If OL9 is gone, this can go. Last checked 2026-11-24: rproxy (the only nginx host) is OL 9.9, and AppStream still has nginx module streams 1.22/1.24/1.26. Still needed until rproxy moves to OL10.

## configure_nvidia_driver

- **udev rule creates `/dev/nvidia*` at boot** (`roles/configure_nvidia_driver/files/70-nvidia.rules`)
  - Why (inferred): the `.run` installer doesn't create the device nodes on a headless host, and LXC GPU passthrough needs them to exist with open permissions.
  - Check: boot without the rule, then `ls -l /dev/nvidia*`.
- **`--allow-installation-with-running-driver`** (`roles/configure_nvidia_driver/tasks/main.yml:79`)
  - Why (inferred): the installer refuses while the module is loaded or used by LXC guests.
  - Check: run the installer without it on a host where the driver is loaded.
- **nvidia-persistenced installed from the driver's samples** (`roles/configure_nvidia_driver/tasks/main.yml:103`)
  - Why (inferred): the `.run` installer doesn't install a systemd unit for it.
  - Check: `systemctl cat nvidia-persistenced` straight after a fresh install. Last checked 2026-11-24: the unit was `failed` on pvematt since the 2026-11-08 boot, but only because no nvidia module existed for that kernel. The role passed `--dkms` without installing `dkms`, so the build only covered the running kernel. Fixed by installing `dkms` and `proxmox-default-headers`.

## configure_opnsense_syslog

- **`reload: true` on the syslog module** (`roles/configure_opnsense_syslog/tasks/main.yml:18`)
  - Why: `oxlorg.opnsense.syslog` defaults `reload` to false, which saves the destination but never applies it to syslog-ng.
  - Check: the collection's changelog for a default change.

## configure_package_manager

- **archlinux-keyring rescue** (`roles/configure_package_manager/tasks/01-archlinux-26.yml:11`)
  - Why (inferred): signature or keyring failures on Arch installs that haven't been updated in a while; the rescue re-inits and refreshes the keyring, then retries.
  - Check: whether the rescue ever fires (`-v` output).
- **makepkg `!debug` drop-in** (`roles/configure_package_manager/tasks/01-archlinux-26.yml:28`)
  - Why: pacman 6.1+ ships `OPTIONS=(... debug ...)` and builds `-debug` packages for every AUR build. Since 2026-11-24 this is `/etc/makepkg.conf.d/no-debug.conf` with `OPTIONS+=(!debug)`, where it used to rewrite the whole vendor line. makepkg's `in_opt_array` takes the last match.
  - Check: `grep ^OPTIONS /etc/makepkg.conf` on a fresh Arch. Last checked 2026-11-24 (pacman 7.1): stock still has `debug`.
- **ol10_appstream added on OL10** (`roles/configure_package_manager/tasks/01-oraclelinux-10.yml:16`)
  - Why: the minimal OL10 LXC image only ships baseos.
  - Check: `ls /etc/yum.repos.d/` on a fresh OL10 LXC template. Last checked 2026-11-24 (linuxcontainers build 20261112): still only `base.repo` and `base_latest.repo`, both baseos.

## configure_packages

- **iotop → iotop-c migration** (`roles/configure_packages/tasks/01-all.yml:5`, marked TEMP)
  - Why: iotop-c only provides `iotop`, so the old package conflicts.
  - Check: `rpm -q iotop` / `dpkg -l iotop` on every host. Once none have it, delete the tasks. Last checked 2026-11-24: gone from all 15 reachable hosts. x230t (Manjaro), musicass (Raspbian) and bigbilly (Debian) were unreachable and could still have it.
- **neofetch fallback for fastfetch** (`roles/configure_packages/tasks/04-fastfetch.yml:2`)
  - Why (inferred): fastfetch isn't packaged on older distros.
  - Check: `dnf info fastfetch` / `apt-cache policy fastfetch` on each host.

## configure_postfix_gmail

- **Distro `main.cf` keys commented out** (`roles/configure_postfix_gmail/tasks/main.yml:48`)
  - Why (inferred): stops duplicate keys conflicting with the blockinfile. `postconf -e` would be cleaner.
  - Check: `postconf -n` and `postfix check` warnings. Last checked 2026-11-24 (Postfix 3.10, pvematt/pvewill): no duplicate keys. The only warning was the deprecated `smtp_use_tls`, which was redundant with `smtp_tls_security_level = encrypt` and is now dropped from the block.
- **Empty `smtp_sasl_security_options`** (`roles/configure_postfix_gmail/tasks/main.yml:64`)
  - Why (inferred, from the gist it's based on): turns off `noplaintext,noanonymous` so Gmail's PLAIN login works. It also allows anonymous mechanisms.
  - Check: set it to `noanonymous` and send a test mail.

## configure_pve

- **pve-nag-buster** (`roles/configure_pve/tasks/01-repos.yml:10`)
  - Why: removes Proxmox's subscription nag and switches repos. Could break silently on a new PVE major, e.g. if repos move to deb822 `.sources`.
  - Check: is upstream still maintained, and does the nag come back after `apt install --reinstall proxmox-widget-toolkit`? Last checked 2026-11-24 (PVE 9.2, widget-toolkit 5.2.13): still works. The dpkg hook re-patched `proxmoxlib.js` on 2026-11-18 after the toolkit update (the check now reads `res.false`), and the repos are `pve-no-subscription` with no enterprise `.sources`. Upstream's last commit was 2021-05, so it works because Proxmox hasn't changed that line, not because it's maintained.

## configure_pvpn

- **Fake `appversion` fetched from GitHub** (`roles/configure_pvpn/files/pvpn-select/pvpn_select.py:22`)
  - Why: Proton rejects old app versions. If GitHub is unreachable or the file format changes, the script crashes at import.
  - Check: run it with a fixed old version string. Last checked 2026-11-24: `versions.yml` on `stable` still starts with `version: 6.1.2` (2026-11-06), parses to `linux-vpn-cli@6.1.2+x86_64`. The old-version test wasn't run, since it needs a real Proton login.
- **proton-core installed from git** (`roles/configure_pvpn/files/pvpn-select/pyproject.toml:5`)
  - Why: the PyPI `proton-core` is a 0.0.1 placeholder.
  - Check: `pip index versions proton-core`. Last checked 2026-11-24: still only 0.0.1 with no files, and v0.7.4 is still the newest upstream tag.
- **tailscaled on port 41642** (`roles/configure_pvpn/tasks/main.yml:53`)
  - Why: OPNsense's own Tailscale uses 41641 on the same public IPv4.
  - Check: only needed while OPNsense runs Tailscale. Last checked 2026-11-24: `kg-opnsense` (FreeBSD) is still on the tailnet and offers an exit node, and pvpn's tailscaled is on 41642.
- **`ip rule del … || true` before adding** (`roles/configure_pvpn/templates/wg0.conf.j2:13`)
  - Why: wg-quick runs hooks with `set -e`, and `ip rule` has no idempotent replace.
  - Check: iproute2 gaining `ip rule replace`. Last checked 2026-11-24: still only `add | del` in iproute2 6.17 (pvpn) and 7.3 (Debian sid).

## configure_reverse_proxy

- **certbot rate-limit errors ignored** (`roles/configure_reverse_proxy/tasks/03-configure-certbot.yml:31`)
  - Why (inferred): Let's Encrypt's "too many certificates" rate limit otherwise fails the run. It also hides that the cert wasn't renewed.
  - Check: `grep -i "too many" /var/log/letsencrypt/letsencrypt.log*`. Last checked 2026-11-24: no hits in 67 logs, and the cert is valid until 2027-02-18 (`certbot_renew.timer` renews it). The Ansible run only issues a cert when `/etc/letsencrypt` is fresh, i.e. on a rebuild, which is when the 5-per-week duplicate limit hits, so it's worth keeping for rebuild loops.
- **Empty `options-ssl-nginx.conf` if the download fails** (`roles/configure_reverse_proxy/tasks/03-configure-certbot.yml:56`)
  - Why (inferred): the distro certbot here has no nginx plugin, so the file isn't shipped and is pulled from certbot's GitHub `main`. **An empty file silently drops the TLS protocol and cipher settings from every vhost.**
  - Check: `wc -c /etc/letsencrypt/options-ssl-nginx.conf` on rproxy, and whether the GitHub path still resolves. Last checked 2026-11-24: 775 bytes, fine.
- **`proxy_set_header Host $host:443` for stream** (`roles/configure_reverse_proxy/files/hosts/rproxy/sites-available/stream.conf:10`)
  - Why (inferred): the upstream builds absolute URLs from the Host header and gets the port wrong without it.
  - Check: switch to `Host $host` and look at the URLs in `player_api.php` and m3u responses.

## configure_snapraid

- **`sleep 240` then `hd-idle -t` on the parity disks** (`roles/configure_snapraid/templates/snapraid_helper.sh.j2:293`)
  - Why (inferred): the drives or their USB bridge don't follow their own standby timers. The sleep lets final I/O settle before forcing spin-down.
  - Check: remove it and `hdparm -C /dev/disk/by-label/Eiko` a few minutes after a run.

## configure_sshd

- **sshd restarted, not reloaded** (`roles/configure_sshd/handlers/main.yml:2`)
  - Why: on Debian 13 a SIGHUP'd sshd can't rebind while `ssh.socket` holds the port.
  - Check: `systemctl is-enabled ssh.socket` on Debian 13 hosts. Last checked 2026-11-24: disabled on pvematt and pvewill. bigbilly (Debian) and musicass (Raspbian) were unreachable, and those are the hosts the restart is for.
- **RedHat's `01-permitrootlogin.conf` deleted** (`roles/configure_sshd/tasks/01-nonpve.yml:27`)
  - Why (inferred): the EL/OL installer drops in `PermitRootLogin yes`, and sshd takes the first value it reads, so `01-` beats our `90-`.
  - Check: `ls /etc/ssh/sshd_config.d/; sshd -T | grep permitrootlogin` on a fresh OL image. Last checked 2026-11-24: not in the oraclelinux:9/10 images or the OL10 LXC rootfs. It's written by the Anaconda installer's "allow root SSH login" option, so it only matters for ISO installs like gsb (KVM). Keep it while any host is installed from an ISO.

## configure_telegraf

- **telegraf from the AUR on Arch** (`roles/configure_telegraf/tasks/01-pacman.yml:5`)
  - Why: it isn't in the official repos, and yay refuses to run as root.
  - Check: `pacman -Si telegraf`. Last checked 2026-11-24: not in the official repos.
- **`skip_processors_after_aggregators = true`** (`roles/configure_telegraf/templates/telegraf.d/05-agent-common.conf:8`)
  - Why: silences the warning about the default changing in v1.41. There are no aggregators, so the value doesn't matter.
  - Check: once on v1.41+, delete the line and `journalctl -u telegraf | grep skip_processors` should be empty. Last checked 2026-11-24: latest release is v1.40.4, hosts on 1.40.3/1.40.4.
- **`startup_error_behavior = "retry"` on the docker input** (`roles/configure_telegraf/templates/telegraf.d/20-docker.conf:6`)
  - Why: by default one input failing to start (docker down) kills the whole agent.
  - Check: telegraf changing that default. Last checked 2026-11-24 (v1.40.4 `models/running_input.go`): empty still falls through to `"error"`.

## create_opnsense_entries

- **`noqa: jinja[invalid]` on the MAC alias** (`roles/create_opnsense_entries/tasks/3-alias.yml:29`)
  - Why: ansible-lint renders the MAC octets as strings, while a real run gives ints.
  - Check: delete the noqa and run ansible-lint on a newer release. Last checked 2026-11-24 (ansible-lint 26.11.0, ansible-core 2.22.0): still `can only concatenate str (not "int") to str`.
- **`oxlorg.opnsense.raw` for alias categories** (`roles/create_opnsense_entries/tasks/3-alias.yml:48`, `tasks/3-alias-tag.yml`)
  - Why: the alias module can't set categories.
  - Check: `ansible-doc oxlorg.opnsense.alias | grep -i categor` after a collection upgrade. Last checked 2026-11-24 (26.1.11, latest on Galaxy): only `webproxy_remote_acl` mentions categories, the alias module has no support.
- **`selected` compared as int or string** (`roles/create_opnsense_entries/tasks/3-alias-tag.yml:21`)
  - Why (inferred): the OPNsense API returns it as either, inconsistently.
  - Check: `getItem` output types with `-vvv`.

## create_proxmox_ct

- **`lineinfile` into `/etc/pve/lxc/<id>.conf`** (`roles/create_proxmox_ct/tasks/main.yml:43`)
  - Why (inferred): the PVE API, and so `community.proxmox`, won't set raw `lxc.*` keys.
  - Check: whether everything in `proxmox_ct_conf_extra` is settable through module params. Last checked 2026-11-24 (PVE 9.2, community.proxmox 2.1.0): all of it now is. The `mpN` bind mounts (yoho, kismnas) map to `mount_volumes`. The `lxc.cgroup2.devices.allow` + `lxc.mount.entry` pairs for `/dev/net/tun` and `/dev/nvidia*` (pvpn, yoho, stream, jf) map to `mount_devices` (`devN: /dev/...`), which also stops hardcoding nvidia-uvm's dynamic major (511). Not switched yet, it needs a test CT create.

## maintenance_gather_facts_pve / maintenance_shutdown_pve_guests

- **Retries on `proxmox_vm_info`** (`roles/maintenance_gather_facts_pve/tasks/main.yml:12`, `roles/maintenance_shutdown_pve_guests/tasks/main.yml:11`)
  - Why (inferred): the PVE API or root@pam login is occasionally flaky.
  - Check: run logs for "FAILED - RETRYING: … Get Proxmox Guests".

## maintenance_update_packages

- **dnf clean-and-retry rescue** (`roles/maintenance_update_packages/tasks/01-dnf.yml:20`)
  - Why (inferred): corrupt or stale repo metadata.
  - Check: run logs for the rescue ever firing.

## Top-level

- **`serial: 5` in `configure_opensense_for_host.yml`** (`configure_opensense_for_host.yml:5`)
  - Why: Bitwarden Secrets Manager gets overloaded (rate limited) otherwise.
  - Check: run it without `serial` against all hosts and watch for 429s or timeouts from the bws lookup.

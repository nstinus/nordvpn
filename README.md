Nordvpn
=======

Introduction
------------

`nordvpn` is a command line helper script to use nordvpn.com for
systems with `openvpn` and `systemd`.
It was created for Arch Linux but should run without too much
difficulty on systems that satisfy the following dependency list:
- openvpn,
- systemd,
- curl,
- unzip,
- ping,
- openvpn-update-resolv-conf or vpnfailsafe.

Quickstart
----------

- Once installed, run `sudo nordvpn update` to download and install the
configuration files.
- Edit `/etc/openvpn/client/nordvpn/credentials.conf`.
- Run `sudo nordvpn list` to choose a server (alternatively the rank
command pings the servers).
- Finally `sudo nordvpn start <servername>`.
- The status command shows you the status of the systemd service.
- See `sudo nordvpn -h` for mre information.

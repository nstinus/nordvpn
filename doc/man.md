% NORDVPN(8) Version @version@ | Nordvpn command line utility

NAME
====

nordvpn - utility to use nordvpn.com with openvpn and systemd.

SYNOPSIS
========

| **nordvpn** [-v, --verbose] [-h, --help]
| **nordvpn** [-v, --verbose] **start** [-t, --tcp] _server_name_
| **nordvpn** [-v, --verbose] **stop**
| **nordvpn** [-v, --verbose] **restart**
| **nordvpn** [-v, --verbose] **status**
| **nordvpn** [-v, --verbose] **update** [-f, --force]
| **nordvpn** [-v, --verbose] **ping** _server_name_
| **nordvpn** [-v, --verbose] **list** [_server_pattern_]
| **nordvpn** [-v, --verbose] **infos** [-f, --force]
| **nordvpn** [-v, --verbose] **rank** [_server_pattern_]

DESCRIPTION
===========

**nordvpn** is a helper script to manage _openvpn_ connections to the subscription-based VPN service <https://www.nordvpn.com> from which it downloads the configuration files.
Once files are present and credentials are set up (see **FILES** below), it can start, stop, restart and show the status of the systemd running service.
Note that except for **status**, all the commands require super-user privileges.

COMMANDS
--------

**start** [**-t**, **--tcp**] _server_name_

: Start a connection to _server_name_. By default, it will connect in UDP. Use option [**-t**, **--tcp**] for TCP.

**stop**

: Stop the open connection.

**restart**

: Restart the open connection.

**status**

: Show systemd's openvpn running service.

**update** [**-f**, **--force**]

: Download, patch and install openvpn configuration files from nordvpn.com. By default, it will not update unless the files have changed. Use **-f**, **--force** to override this.

**ping** _server_name_

: Show latency to server. Should be used before opening a connection to choose the best one.

**list** [_server_pattern_]

: Show all available servers matching _server_pattern_.

**infos** [**-f**, **--force**]

: Show all available servers currently configured with additional information like current load, location and features. It will store data in /tmp/nordvpn_servers.json. The file is automatically updated after 15 minutes; option [**-f**, **--force**] forces the download. Requires **python** and the **pandas** package.

**rank** [_server_pattern_]

: ping and sort all servers matching _server_pattern_. See _ping_ above.


OPTIONS
-------

-h, --help

: Print usage and exit.

-v, --verbose

: Be more verbose, will trace every shell call. Mainly for debugging.

FILES
=====

*/etc/openvpn/client/nordvpn/credentials.conf*

: Credentials of nordvpn.com subscription. Login on the first line and password on the second.

*/tmp/nordvpn_servers.json*

: Servers list downloaded from https://api.nordvpn.com/server and used by **nordvpn infos**.

BUGS
====

Please report any bug or feature request to GitHub Issues: <https://github.com/nstinus/nordvpn/issues>.

AUTHOR
======

Nicolas Stinus <nicolas.stinus@gmail.com>

SEE ALSO
========

**systemctl(1)**, **openvpn(8)**, **ping(8)**
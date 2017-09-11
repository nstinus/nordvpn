#!/usr/bin/env python

from argparse import ArgumentParser
import os
import json
import sys
import shlex
import re
from subprocess import Popen, PIPE, run


def get_region(available, argument):
    argument = argument.strip().lower()
    if argument in ['eu', 'europe']:
        region = available[available.latitude > 35]
        region = region[region.latitude < 70]
        region = region[region.longitude < 60]
        region = region[region.longitude > -25]
        region = region[[flag not in ['TR']
                         for flag in region.flag]]  # Turkey to NE
    elif argument in ['na', 'northamerica']:
        region = available[[
            flag in ['US', 'CA', 'MX'] for flag in available.flag
        ]]
    elif argument in ['sa', 'southamerica']:
        region = available[available.latitude > 35]
        region = region[region.latitude < 30]
        region = region[region.longitude < -30]
        region = region[region.longitude > -90]
        region = region[[
            flag not in ['US', 'CA', 'MX'] for flag in region.flag
        ]]
    elif argument in ['am', 'americas']:
        region = region[region.longitude < -30]
        region = region[region.longitude > -165]
    elif argument in ['all']:
        region = available
    elif argument in ['ne', 'neareast']:
        region = available[available.latitude > 10]
        region = region[region.latitude < 45]
        region = region[region.longitude < 60]
        region = region[region.longitude > 25]
        region = region[[flag not in ['RO'] for flag in region.flag]]
    elif argument in ['as', 'asia']:
        region = available[available.latitude > -10]
        region = region[region.longitude < 180]
        region = region[region.longitude > 60]
    elif argument in ['oc', 'oceania']:
        region = available[available.latitude < -10]
        region = region[region.longitude < 180]
        region = region[region.longitude > 100]
    else:
        regex = re.compile(argument)
        region = available[[
            bool(regex.search(name)) for name in available.name
        ]]
    return region


def validate_addresses(addresses):
    return [
        i if i.find(".nordvpn.com") > 0 else i + ".nordvpn.com"
        for i in addresses
    ]


def pingservers(addresses, count=1, repeat=True):
    if not isinstance(count, int):
        raise ValueError("Count can only be an integer")
    count = max(1, count)
    callsig = shlex.split(f"fping -q -c {count}")

    addresses = validate_addresses(addresses)

    res = run(
        callsig + addresses, check=False, universal_newlines=True, stderr=PIPE)
    results = {}
    repeats = []
    for line in res.stderr.splitlines():
        server = line.split(":")[0].strip()
        loss = float(line.split("%")[1].split("/")[-1])
        roundtime = float(line.split("=")[-1].split("/")[1].strip())
        results[server.split('.')[0]] = roundtime
        if loss == 100 or roundtime <= 1:
            repeats.append(server)
    if repeat and repeats:
        results.update(pingservers(repeats, count=count + 1, repeat=False))
    return results

def best_function(servers, args):
    # Filter by keywords
    if args.keyword is not None:
        servers = servers[[set(args.keyword).issubset(record) for record in
                         servers.search_keywords]]
    if len(servers) < 1:
        return f"No servers left after filtering according to keywords:\n{args.keyword}" 
    # Filter by load
    servers = servers[servers.load <= args.maxload]
    if len(servers) < 1:
        return f"All filtered servers loaded more than {args.maxload}%. Min load {servers.load.min()}%"
    # Ping (effectively distance without unnecessary permissions)
    pings = pingservers(servers.name.tolist(), count=args.pingcount)
    pinged = servers.join(
        pandas.Series(pings, name='ping'), how='right',
        on='name').sort_values("ping")
    return pinged[:args.num].to_string(index=False, columns=['name', 'country', 'load', 'ping', 'search_keywords'])

if __name__ == "__main__":

    try:
        import pandas
    except:
        import sys
        print("Can't import pandas. Please see 'man nordvpn'.", file=sys.stderr, flush=True)
        sys.exit(1)

    parser = ArgumentParser()
    parser.add_argument("servers_filename")
    parser.add_argument(
        "-f", "--force", action='store_true', default=False)  # just capture
    parser.add_argument("--ranking", action='store_true', default=False)
    parser.add_argument("--maxload", default=99, type=int)
    parser.add_argument("--num", default=20, type=int)
    parser.add_argument("--region", type=str, default='all')
    parser.add_argument("--pingcount", type=int, default=1)
    parser.add_argument("--keyword", type=str, action='append')
    args = parser.parse_args()
    if not os.access(args.servers_filename, os.R_OK):
        print >>sys.stderr, "Can't read {}".format(args.servers_filename)
        sys.exit(1)

    df = pandas.read_json(args.servers_filename)
    df["latitude"] = df.location.apply(lambda x: float(x["lat"]))
    df["longitude"] = df.location.apply(lambda x: float(x["long"]))
    df["name"] = df.domain.apply(lambda x: x.replace(".nordvpn.com", ""))
    features = set()
    for feature in df.features:
        features |= set(feature)
    for feature in features:
        df[feature.replace("openvpn_", "")] = df.features.apply(lambda x: x[feature])
    df.drop(["categories", "domain", "price", "id", "ip_address", "location", "features"], axis=1, inplace=True)
    df = df[df.tcp | df.udp]
    df = df[['name', 'country', 'flag', 'load', 'search_keywords', 'latitude', 'longitude', 'udp', 'tcp', 'xor_udp', 'xor_tcp', 'ikev2']]

    # Cross servers with the installed files
    p1 = Popen(shlex.split('find /etc/openvpn/client/ -type l -name "nordvpn_*.conf"'), stdout=PIPE)
    installed = set([os.path.splitext(os.path.basename(i).strip())[0].decode().split("_")[1] for i in p1.stdout.readlines()])
    available = df[df.name.apply(lambda x: x in installed)]

    servers = get_region(available, args.region)
    if args.ranking:
        print(best_function(servers, args))
    else:
        print(servers.to_string(index=False))

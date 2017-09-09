#!/usr/bin/env python3

if __name__ == "__main__":
    from argparse import ArgumentParser
    import os
    import json
    import sys
    import shlex
    from subprocess import Popen, PIPE

    try:
        import pandas
    except:
        import sys
        print("Can't import pandas. Please see 'man nordvpn'.", file=sys.stderr, flush=True)
        sys.exit(1)

    parser = ArgumentParser()
    parser.add_argument("servers_filename")
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

    print(df[df.name.apply(lambda x: x in installed)].to_string(index=False))

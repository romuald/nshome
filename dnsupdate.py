#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socket
import urllib2

from argparse import ArgumentParser, FileType
from subprocess import Popen, PIPE

IPHOST = 'ip.bit.fr'

SCRIPT = """SERVER %(server)s
UPDATE DELETE %(name)s A
UPDATE ADD %(name)s %(ttl)d A %(ip)s
%(show)sSEND"""

def parseargs():
    parser = ArgumentParser(description='Update a DNS zone with your '
                            'IP address, using nsupdate',
                            conflict_handler='resolve')
    parser.add_argument('-k', '--key', type=FileType('rb', 0), required=True,
                        help='Private key used to sign your update request')
    parser.add_argument('-n', '--name', required=True,
                        help='The hostname you wish to update (need FQDN)')
    parser.add_argument('-s', '--server', required=True,
                        help='The target DNS server')
    parser.add_argument('-t', '--ttl', type=int, default=300,
                        help='TTL of record (default 5min)')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        default=False, help='Be verbose')

    return parser.parse_args()

def get_ip():
    # Force IPv4
    host4 = socket.gethostbyname(IPHOST)
    req = urllib2.Request('http://{}/'.format(host4),
                          headers = {'Host': IPHOST})

    ip = urllib2.urlopen(req).read(128)
    if ip.count('.') != 3:
        raise RuntimeError('%r not an IPv4?' % (ip, ))

    return ip.strip()

def main():
    args = parseargs()
    data = {
        'ip': get_ip(),
        'show': 'SHOW\n' if args.verbose else '',
    }
    data.update(vars(args))
    script = SCRIPT % data

    run = ['nsupdate', '-k', args.key.name]
    if args.verbose:
        print "%% %s\n===\n%s\n===" % (' '.join(run), script)

    proc = Popen(run, stdin=PIPE)
    proc.stdin.write(script)
    proc.stdin.flush()
    proc.stdin.close()
    proc.wait()

if __name__ == '__main__':
    main()

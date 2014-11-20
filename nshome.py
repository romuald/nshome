#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script is used to send dynamic updates to a DNS server
to update a record to your IP address.

Mainly useful for people with dynamic IP providers who
have access to a customised DNS server
"""
import json
import socket
import urllib2

from time import sleep, strftime
from argparse import ArgumentParser, FileType
from subprocess import Popen, PIPE

IPHOST = 'ip.bit.fr'

SCRIPT = """SERVER %(server)s
UPDATE DELETE %(name)s A
UPDATE ADD %(name)s %(ttl)d A %(ip)s
%(show)sSEND
"""

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
    parser.add_argument('-p', '--poll', type=int, default=0,
                        help='Check for IP change every POLL minutes')

    return parser.parse_args()

def get_ip():
    """Retrieve ip from remote service"""
    # Force IPv4
    host4 = socket.gethostbyname(IPHOST)
    req = urllib2.Request('http://{}/'.format(host4),
                          headers = {'Host': IPHOST})

    ip = urllib2.urlopen(req).read(128)
    if ip.count('.') != 3:
        raise RuntimeError('%r not an IPv4?' % (ip, ))

    return ip.strip()

def do_update(ip, args):
    data = {
        'ip': ip,
        'show': 'SHOW\n' if args.verbose else '',
    }
    data.update(vars(args))
    script = SCRIPT % data

    run = ['nsupdate', '-k', args.key.name]
    if args.verbose:
        print "%s %% %s\n===\n%s\n===" % (now(), ' '.join(run), script.strip())

    proc = Popen(run, stdin=PIPE)
    proc.stdin.write(script)
    proc.stdin.flush()
    proc.stdin.close()

    return proc.wait() == 0

def now():
    # lazy
    return strftime("%Y-%m-%d %H:%M:%S")

def main():
    args = parseargs()

    ip_prev = None
    while True:
        try:
            ip = get_ip()
        except (socket.error, urllib2.HTTPError):
            print 'unable to retrieve IP address'
            ip = None

        if ip and ip != ip_prev:
            print "%s IP changed to %s -> UPDATE" % (now(), ip)
            if do_update(ip, args):
                # If update failed, try again next time, don't wait for IP change
                ip_prev = ip

        if args.poll <= 0:
            break

        try:
            sleep(60 * args.poll)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()

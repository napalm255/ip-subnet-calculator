#!/usr/bin/env python
"""IP Subnet Calculator."""

from __future__ import print_function
import json
import netaddr
from netaddr import IPAddress, IPNetwork


def handler(event, context):
    """Lambda handler."""
    # pylint: disable=unused-argument, invalid-name

    output = {'statusCode': 200,
              'body': '',
              'headers': {'Content-Type': 'application/json',
                          'Access-Control-Allow-Origin': '*',
                          'Access-Control-Allow-Methods': 'GET'}}

    try:
        ipaddy = event['query']
        assert ipaddy != ''
    except KeyError:
        web = open('ipcalc.html', 'r')
        output['body'] = web.read()
        output['headers']['Content-Type'] = 'text/html'
        return output
    except AssertionError:
        web = open('ipcalc.html', 'r')
        output['body'] = web.read()
        output['headers']['Content-Type'] = 'text/html'
        return output

    if ' ' in ipaddy:
        ip_parts = ipaddy.split(' ')
        pos1 = IPAddress(ip_parts[0])
        pos2 = IPAddress(ip_parts[1])
        if pos2.is_netmask():
            ipaddy = '%s/%s' % (pos1, pos2.netmask_bits())
    elif '/' not in ipaddy:
        ipaddy = '%s/32' % ipaddy

    try:
        ip = IPNetwork(ipaddy)
        ip_hosts = int(ip.size) - 2
        hostmin = ip.cidr[1] if len(ip.cidr) > 1 else ip.cidr[-1]
        hosts = len(ip.cidr) - 2 if len(ip.cidr) > 1 else 1
        results = {'input': str(ipaddy),
                   'event': event,
                   'version': str(ip.version),
                   'private': ip.is_private(),
                   'reserved': ip.is_reserved(),
                   'prefixlen': str(ip.prefixlen),
                   'address': str(ip.ip),
                   'network': str(ip.network),
                   'netmask': str(ip.netmask),
                   'wildcard': str(ip.hostmask),
                   'hostmin': str(hostmin),
                   'hostmax': str(ip.cidr[ip_hosts]),
                   'broadcast': str(ip.broadcast),
                   'hosts/net': str(hosts)}
    except netaddr.AddrFormatError as errstr:
        results = {'error': '%s' % errstr}

    output['body'] = json.dumps(results)
    return json.dumps(results)


if __name__ == "__main__":
    print(handler({'query': '192.168.1.69'}, None))
    print(handler({'query': '192.168.0.2/23'}, None))
    print(handler({'query': '192.168.0.3 255.255.252.0'}, None))
    print(handler({'query': '192.168.d.a'}, None))
    print(handler({'query': '45824759'}, None))
    print(handler({'query': ''}, None))
    print(handler({}, None))

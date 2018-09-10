#!/usr/bin/env python
"""
Reads one or more NMAP XML output files and groups the hosts by port number.

author: https://github.com/lorenzog

"""
from __future__ import print_function
import argparse
from collections import defaultdict
import sys
from lxml import etree


def do_parse(the_file, tcp=None, udp=None, requested_ports=None,
             filter_expression=None):
    ports = defaultdict(list)
    try:
        r = etree.ElementTree(file=the_file)
    except etree.XMLSyntaxError as e:
        print("Error in %s: %s" % (the_file, e), file=sys.stderr)
        return ports
    # search for open ports; get the parent of the ports with 'state'='open'
    all_ports = r.xpath('//*/port/state[@state="open"]/..')
    for port in all_ports:
        if filter_expression is not None:
            try:
                is_valid = port.findall(filter_expression)
                if len(is_valid) == 0:
                    # the filter expression removed all results. skip..
                    continue
            except SyntaxError as e:
                raise SystemExit(e)
        port_number = port.get('portid')
        if len(requested_ports) > 0 and port_number not in requested_ports:
            # skip ports that aren't requested
            continue
        protocol = port.get('protocol')
        if tcp is True and protocol != 'tcp':
            if udp is False:
                # if udp is True, maybe it's a requested udp port (e.g. 53/udp)
                continue
        if udp is True and protocol != 'udp':
            if tcp is False:
                continue
        # get the grandparent's IP address
        # hacky, but there's always one..
        address = port.xpath('../../address[@addrtype="ipv4"]')[0].get('addr')
        # key: port/proto e.g. 53/udp
        ports['{}/{}'.format(port_number, protocol)].append(address)

    return ports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('the_file', nargs='+')
    parser.add_argument('-u', '--udp', action='store_true')
    parser.add_argument('-t', '--tcp', action='store_true')
    parser.add_argument('-p', '--port', action='append', default=[])
    parser.add_argument(
        '-o',
        '--output',
        help=("Output into files PORT_PROTO.txt containing "
              "the list of hosts (will overwrite)"),
        action='store_true'
    )
    parser.add_argument(
        '-f',
        '--filter-expression',
        help="A valid XPATH to filter results such as:\n\t'*[@ostype=\"Windows\"]' \n\t'service[@name=\"https\"]'"
    )
    args = parser.parse_args()

    discovered = defaultdict()
    for f in args.the_file:
        print("Parsing %s" % args.the_file)
        ports = do_parse(
            f,
            tcp=args.tcp,
            udp=args.udp,
            requested_ports=args.port,
            filter_expression=args.filter_expression
        )
        discovered.update(ports)

    filenames = list()
    for k, v in discovered.items():
        print('{}: {}'.format(k, v))
        if args.output:
            _filename = '{}.txt'.format(k.replace('/', '_'))
            with open(_filename, 'w') as f:
                f.write('\n'.join(v))
                f.write('\n')
            filenames.append(_filename)

    if len(filenames) > 0:
        print("Written output to files: {}".format(' '.join(filenames)))


if __name__ == '__main__':
    main()

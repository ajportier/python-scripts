#!/usr/bin/python
# Author: Adam Portier <ajportier@gmail.com>
# Purpose: Reads an ISC DHCP configuration and .db file and determines how many
# addresses for each configured pool can still be assigned

import netaddr
import sys
import re

dhcp_conf = 'dhcpd.conf'
dhcp_db = 'dhcp.db'

if __name__ == '__main__':
    # reads the first value (the IP) from each line in the db file into an array
    dhcp_ips = [l.rstrip().split()[0] for l in open(dhcp_db,'rb').readlines()]
    dhcp_networks = {}
    dhcp_conf_l = [l.rstrip() for l in open(dhcp_conf,'rb').readlines()]
    network = ''
    
    # runs through the dhcp configuration and turns the dynamic ranges into
    # lists of IPAddress objects, put in a dict keyed by their containing subnet
    for l in dhcp_conf_l:
        m = re.search('subnet\s+(\S+)\s+netmask\s+(\S+)\s+\{',l)
        if m:
            subnet = m.group(1)
            netmask = m.group(2)
            network = str(netaddr.IPNetwork(subnet,netmask))
            dhcp_networks.update({network:[]})
        m = re.search('dynamic\-dhcp\s+range\s+(\S+)\s+(\S+)\s+\{',l)
        if m:
            start_ip = m.group(1)
            end_ip = m.group(2)
            ip_range = list(netaddr.iter_iprange(start_ip,end_ip))
            dhcp_networks[network] += ip_range

    # runs through the list of IPs found in the dhcp.db file and removes them
    # from the list of available IPs in the networks dict if found
    for ipaddr in dhcp_ips:
        for network in dhcp_networks.keys():
            if netaddr.IPAddress(ipaddr) in netaddr.IPNetwork(network):
                print "{} in {}".format(ipaddr,network)
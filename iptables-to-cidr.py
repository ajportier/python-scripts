#!/usr/bin/python
# Reads in an iptables configuration and prints all the CIDR format networks
# being accepted

import netaddr
import sys
import re

try:
    f = open(sys.argv[1])
except:
    sys.exit('No file specified')

accept_subnet = re.compile('\-A\s+INPUT\s+\-s\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

subnet_list = re.findall(accept_subnet, f.read())
for subnet in subnet_list:
    ip = netaddr.IPNetwork(subnet)
    print ip.cidr

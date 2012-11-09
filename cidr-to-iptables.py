#!/usr/bin/python
# Reads in a list of CIDR network definitions and prints out iptables ACCEPT
# rules to cover them

import netaddr
import sys

try:
    f = open(sys.argv[1])
except:
    sys.exit('No file specified')

for line in f:
    subnet = netaddr.IPNetwork(line)
    print '-A INPUT -s {}/{} -m state --state NEW -j ACCEPT'.format(str(subnet.ip), str(subnet.netmask))

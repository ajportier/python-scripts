#!/usr/bin/python
# Reads in a file of one-line CIDR networks and an IP address and prints if the
# address is covered by any of the networks

import sys
import netaddr

try:
    f = open(sys.argv[1])
except:
    sys.exit('No file specified')

try:
    ipaddr = netaddr.IPAddress(sys.argv[2])
except:
    sys.exit('No ipaddr given')

ipset = netaddr.IPSet()

for line in f:
    ipset.add(str(line))

print ipaddr in ipset

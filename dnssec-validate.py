#!/usr/bin/python
# Author: Adam Portier <adam_portier@cable.comcast.com>
# Purpose: Verify the RRSIGs of a provided domain against the DS stored in the parent and
# The DNSKEYs stored in the zone



import argparse
import sys
import dns.resolver
import dns.name
import struct
import time



__default_ns__ = '8.8.8.8'



def getDomainSOA(domain_name):
    '''Returns the set of SOA records for the given domain using the
    default system resolver'''

    resolver = dns.resolver.Resolver()
    resolver.use_edns(0,dns.flags.DO,4096)
    resolver.nameservers=([__default_ns__])

    if (domain_name == '.'):
        return domain_name
    query_domain_parts = domain_name.split('.')
    query_domain = '.'.join(query_domain_parts)
    try:
        soa_response = resolver.query(query_domain, 'SOA')
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        query_domain_parts.pop(0)
        query_domain = '.'.join(query_domain_parts)
        domain_name = getDomainSOA(query_domain)
    return domain_name



def getNS(domain_name):
    '''Returns all IPs for all NS for the given domain using the
    system default resolver'''

    resolver = dns.resolver.Resolver()
    resolver.use_edns(0,dns.flags.DO,4096)
    resolver.nameservers=([__default_ns__])

    return_ns = set()

    try:
        response_ns = resolver.query(domain_name, 'NS')
    except dns.resolver.NoAnswer:
        print "no answer returned"
    except dns.resolver.NXDOMAIN:
        print "NXDOMAIN"

    for ns in response_ns:
        try:
            response_a = resolver.query(ns.target, 'A')
        except dns.resolver.NoAnswer:
            print "no answer returned"
        except dns.resolver.NXDOMAIN:
            print "NXDOMAIN"
        for a in response_a:
            return_ns.add(a.address)

    return return_ns



def getDSFromNS(domain_name, name_server):
    '''Return the set of DS records for the given domain, as obtained
    from the given server'''

    resolver = dns.resolver
    resolver.nameservers = ([name_server])
    try:
        response_ds = resolver.query(domain_name, 'DS')
    except resolver.NoAnswer:
        print 'no answer returned'
    except resolver.NXDOMAIN:
        print 'NXDOMAIN'
    return response_ds



def getDNSKEYFromNS(domain_name, name_server):
    '''Return the set of DNSKEY records for the given domain, as obtained from
    the given server'''

    resolver = dns.resolver.Resolver()
    resolver.use_edns(0,dns.flags.DO,4096)
    resolver.nameservers = ([name_server])
    name = dns.name.from_text(domain_name)
    rdtype = dns.rdatatype.DNSKEY
    rdclass = dns.rdataclass.IN

    try:
        response = resolver.query(name, rdtype, rdclass, True).response
        response_rrkey = response.find_rrset(response.answer, name, rdclass, dns.rdatatype.RRSIG, rdtype)
        response_dnskey = response.find_rrset(response.answer, name, rdclass, rdtype)
    except dns.resolver.NoAnswer:
        print 'no answer returned'
    except dns.resolver.NXDOMAIN:
        print 'NXDOMAIN'
    return (response_dnskey, response_rrkey)



def getRecordFromNS(domain_name, record, name_server):
    '''Return the set of DNSKEY records for the given domain, as obtained from
    the given server'''

    resolver = dns.resolver.Resolver()
    resolver.use_edns(0,dns.flags.DO,4096)
    resolver.nameservers = ([name_server])
    name = dns.name.from_text(domain_name)
    rdtype = dns.rdatatype.from_text(record)
    rdclass = dns.rdataclass.IN

    try:
        response = resolver.query(name, rdtype, rdclass, True).response
        response_rrkey = response.find_rrset(response.answer, name, rdclass, dns.rdatatype.RRSIG, rdtype)
        response_rrset = response.find_rrset(response.answer, name, rdclass, rdtype)
    except dns.resolver.NoAnswer:
        response_rrset, response_rrkey = getRecordFromNS(domain_name, 'CNAME', name_server)
    except dns.resolver.NXDOMAIN:
        print 'NXDOMAIN'

    return (response_rrset, response_rrkey)



def getExpiredRRSIG(rrset):
    '''Return the set of RRSIG records in the given rrset that have expired'''

    expired_rrsig = set()

    for rrsig in rrset:
        sig_expire = rrsig.expiration
        if len(str(sig_expire)) == 14:
            time_now = int(time.strftime("%Y%m%d%H%M%S",time.gmtime()))
        else:
            time_now = int(time.time())            
        time_diff = sig_expire - time_now
        if time_diff <= 0:
            expired_rrsig.add(rrsig)
    return expired_rrsig



def getKeyTag(rdata):
    '''Return the key_tag for the given DNSKEY rdata, as specified in RFC 4034.'''

    if rdata.algorithm == 1:
        return struct.unpack('!H', rdata.key[-3:-1])[0]

    key_str = struct.pack('!HBB', rdata.flags, rdata.protocol, rdata.algorithm) + rdata.key

    ac = 0
    for i in range(len(key_str)):
        b, = struct.unpack('B',key_str[i])
        if i & 1:
            ac += b
        else:
            ac += (b << 8)

    ac += (ac >> 16) & 0xffff
    return ac & 0xffff



def main():
    parser = argparse.ArgumentParser(
            description='Uses dnpython to validate a single domain')
    parser.add_argument('domain', metavar='DOMAIN', type=str, help='domain to look up')
    args = parser.parse_args()

    domain = args.domain
    if domain.endswith('.') == False:
        domain = domain + '.'

    parent_ns = set()
    child_ns = set()
    domain_ds = set()
    domain_dnskey = set()
    domain_dnskey_rrsig = set()
    expired_dnskey_rrsig = set()
    valid_dnskey = set()
    record_rrset = set()
    record_rrset_rrsig = set()
    expired_rrset_rrsig = set()
    valid_rrset_rrsig = set()

    # Step 1 - Break down the domain into segments and determine the parent domain
    domain_parts = domain.split('.')
    record = domain_parts.pop(0)
    child_domain = '.'.join(domain_parts)

    # Locate the fqdn containing the SOA of both the parent and child domains
    child_domain = getDomainSOA(domain)
    domain_parts = child_domain.split('.')
    domain_parts.pop(0)
    parent_domain = getDomainSOA('.'.join(domain_parts))

    print "Child Domain: " + child_domain
    print "Parent Domain: " + parent_domain

    # Determine the nameservers for the parent domain
    parent_ns = getNS(parent_domain)

    # Determine the nameservers for the requested domain
    child_ns = getNS(child_domain)

    # Query parent domain nameservers for DS records of the requested domain
    # TODO: Verify response is the same from all name servers
    for ns in parent_ns:
        response_ds = getDSFromNS(child_domain, ns)
        for ds in response_ds:
            domain_ds.add(ds.key_tag)

    # Query requested domain nameservers for DNSKEY and RRSIG records
    # TODO: Verify response is the same from all name servers
    for ns in child_ns:
        response_dnskey, response_dnskey_rrsig = getDNSKEYFromNS(child_domain, ns)
        for dnskey in response_dnskey:
            domain_dnskey.add(getKeyTag(dnskey))
        for rrsig in response_dnskey_rrsig:
            domain_dnskey_rrsig.add(rrsig.key_tag)
                
        response_expired_rrsig = getExpiredRRSIG(response_dnskey_rrsig)
        for rrsig in response_expired_rrsig:
            print "DNSKEY RRSIG " + str(rrsig.key_tag) + " has expired"
            expired_dnskey_rrsig.add(rrsig.key_tag)
        
    # Verify that DS and DNSKEY records match up, are signed and signatures have not expired
    valid_dnskeys = domain_ds.copy()
    valid_dnskeys.intersection_update(domain_dnskey)
    valid_dnskeys.intersection_update(domain_dnskey_rrsig)
    valid_dnskeys.difference_update(expired_dnskey_rrsig)
    if len(valid_dnskeys) == 0:
        print "No valid DNSKEYS for this domain"
    else:
        for dnskey in valid_dnskeys:
            print "Valid DNSKEY: " + str(dnskey)
   
    # Verify the RRSIG covering the requsted domain records is signed and has not expired
    for ns in child_ns:
        response_rrset, response_rrset_rrsig = getRecordFromNS(domain, 'A', ns)
        for record in response_rrset:
            record_rrset.add(record)
        for rrsig in response_rrset_rrsig:
            valid_rrset_rrsig.add(rrsig.key_tag)
            record_rrset_rrsig.add(rrsig)

    response_expired_rrsig = getExpiredRRSIG(record_rrset_rrsig)
    for rrsig in response_expired_rrsig:
        print "RRset RRSIG " + str(rrsig.key_tag) + " has expired"
        expired_rrset_rrsig.add(rrsig.key_tag)

    print "Domain DNSKEY: " + str(domain_dnskey)
    print "DNSKEY RRSIG: " + str(domain_dnskey_rrsig)
    print "RRSet RRSIG: " + str(valid_rrset_rrsig)

    valid_rrset_rrsig.intersection_update(valid_dnskeys)
    valid_rrset_rrsig.difference_update(expired_rrset_rrsig)
    if len(valid_rrset_rrsig) == 0:
        print "No valid RRset RRSIGs for this domain"
    else:
        for rrsig in valid_rrset_rrsig:
            print "Valid RRSIG: " + str(rrsig)




# Boilerplate stub to launch main
if __name__ == '__main__':
    main()

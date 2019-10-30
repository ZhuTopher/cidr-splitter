import ipaddress
#import numpy

# 'ipaddress.ip_address.packed' is more succinct, but using the following
# functions from 'socket' instead for forward-backward conversion clarity
from socket import inet_aton, inet_ntoa

# just including this in order to print Python bytes as raw hex characters
# (and not auto-encoded to ASCII/UTF characters)
from binascii import hexlify, unhexlify

'''
NOTE: ipaddress.ip_network.overlaps and ipaddress.ip_network.address_exclude
are pretty much exactly what I'm looking for; but I need to do this manually
since I want to convert this code to other languages (i.e: Java) which are
not as fortunate ;(
'''

''' HELPER FUNCTIONS '''
# just using native Python implementations; see `manual-imply.py` otherwise

def get_cidr_first_addr(cidr):
    return cidr.network_address

def get_cidr_last_addr(cidr):
    return cidr.broadcast_address

def sort_cidrs(cidrs):
    return sorted(cidrs)

''' MAIN CODE '''
# Given two IP addresses, `low` & `high`, create a (sorted) list of CIDR
# ranges (and individual IPs if necessary) which equate to that IP range
def create_cidrs_from_ip_range(low, high):
    print('stub')
    return [(low, high)]

# this function is going to be operating on the byte level for these addresses
# - again for exercise
def split_cidr_by_exclusion(src_cidr, exclude_cidr):
    src_low = int.from_bytes(inet_aton(str(get_cidr_first_addr(src_cidr))), byteorder='big', signed=False)
    src_high = int.from_bytes(inet_aton(str(get_cidr_last_addr(src_cidr))), byteorder='big', signed=False)

    exclude_low = int.from_bytes(inet_aton(str(get_cidr_first_addr(exclude_cidr))), byteorder='big', signed=False)
    exclude_high = int.from_bytes(inet_aton(str(get_cidr_last_addr(exclude_cidr))), byteorder='big', signed=False)

    ip_ranges = []
    low = src_low

    # TODO: Handle boundary edges more carefully; currently including erroneous IPs
    # assumes src_low <= src_high and exclude_low <= exclude_high
    #print('src_low: %s' % inet_ntoa(int.to_bytes(src_low, length=4, byteorder='big', signed=False)))
    #print('src_high: %s' % inet_ntoa(int.to_bytes(src_high, length=4, byteorder='big', signed=False)))
    #print('exclude_low: %s' % inet_ntoa(int.to_bytes(exclude_low, length=4, byteorder='big', signed=False)))
    #print('exclude_high: %s' % inet_ntoa(int.to_bytes(exclude_high, length=4, byteorder='big', signed=False)))
    loop = True
    while loop:
        #print('low: %s' % inet_ntoa(int.to_bytes(low, length=4, byteorder='big', signed=False)))
        if low < exclude_low:
            old_low = low
            if exclude_low > src_high:
                low = src_high
                loop = False
                # ^ exit on repetition
            else:
                low = exclude_low
            ip_ranges.append((old_low, low))
            continue
        # else: anything below is a candidate for exclusion

        if low < exclude_high:
            if exclude_high < src_high:
                low = exclude_high
            else:
                low = src_high
            continue
        # else: anything below is not selected for exclusion

        if low <= src_high:
            ip_ranges.append((low, src_high))
            loop = False
            # ^ exit on repetition

    src_after_excluded_cidrs = []
    for range in ip_ranges:
        src_after_excluded_cidrs += create_cidrs_from_ip_range(
            inet_ntoa(int.to_bytes(range[0], length=4, byteorder='big', signed=False)),
            inet_ntoa(int.to_bytes(range[1], length=4, byteorder='big', signed=False))
        )

    return src_after_excluded_cidrs

def main(src_cidrs, exclude_cidrs):
    src_cidrs = sort_cidrs(src_cidrs)
    exclude_cidrs = sort_cidrs(exclude_cidrs)
    print(src_cidrs)
    print(exclude_cidrs)

    # double-traversal while-loops
    print(split_cidr_by_exclusion(src_cidrs[1], exclude_cidrs[0]))

# Assumes that there are no individual addresses mixed in with CIDRs
# - i.e: individual addresses should be /32 CIDRs
# - conveniently the Python library 'ipaddress' assumes /32 if no subnet mask is provided
# Assumes that no source subnets nor exclusions self-overlap
# - Allows an exclusion to entirely contain a source subnet &
#   hence allows one exclusion to overlap multiple subnets
if __name__ == '__main__':
    # 192.168.2.0-192.168.2.255 -- eg: a private home network
    # 172.16.5.1 -- eg: a private network's nameserver
    # 10.0.14.0-10.0.17.255 -- eg: a subnet of an enterprise's private network
    src = [ipaddress.ip_network('192.168.2.0/24'),
           ipaddress.ip_network('172.16.5.1/32'),
           ipaddress.ip_network('10.0.14.0/23'),
           ipaddress.ip_network('10.0.16.0/23')]

    # exclude 192.168.2.0-192.168.2.1 -- exclusion trims front entries of src
    # exclude 10.0.16.0-10.0.16.255 -- src is superset of exclusion
    # exclude the entire 172.16.0.0 private IP range -- exclusion is superset of src
    exclude = [ipaddress.ip_network('192.168.2.0/31'),
               ipaddress.ip_network('10.0.16.0/24'),
               ipaddress.ip_network('172.16.0.0/12')]

    main(src, exclude)

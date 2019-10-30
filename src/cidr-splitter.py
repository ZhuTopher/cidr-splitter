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

def compare_ips(ip_a, ip_b):
    if ip_a < ip_b:
        return -1
    if ip_a > ip_b:
        return 1
    return 0

def sort_cidrs(cidrs):
    return sorted(cidrs)

''' MAIN CODE '''
# Given two IP address strings, `low` & `high`, create a (sorted) list of CIDR
# ranges (and individual IPs if necessary) which equate to that IP range
def create_cidrs_from_ip_range(low, high):
    print('stub')
    return [(low, high)]

# this function is going to be operating on the byte level for these addresses
# - again for exercise
def split_cidr_by_exclusion(src_cidr, exclude_cidr):
    src_entirely_excluded = True

    src_low = get_cidr_first_addr(src_cidr)
    src_high = get_cidr_last_addr(src_cidr)

    exclude_low = get_cidr_first_addr(exclude_cidr)
    exclude_high = get_cidr_last_addr(exclude_cidr)

    ip_ranges = []
    low = src_low

    # TODO: Handle edge cases more carefully (/32 CIDRs, exclusion superset src, etc.)
    # - currently including erroneous IPs
    # assumes src_low <= src_high and exclude_low <= exclude_high
    print('src_low: %s' % src_low)
    print('src_high: %s' % src_high)
    print('exclude_low: %s' % exclude_low)
    print('exclude_high: %s' % exclude_high)

    # one-pass CIDR splitting
    # - using `while` + `break` for control-flow (`goto` label behaviour)
    while True:
        # Capture [src_low, exclude_low)
        if compare_ips(low, exclude_low) < 0:
            src_entirely_excluded = False

            old_low = low
            if compare_ips(src_high, exclude_low) < 0:
                # exclusion doesn't intersect
                break
            else:
                low = exclude_low
            # `low-1` is subtraction on an IP Address; eg: 10.0.2.0 - 1 = 10.0.1.255
            ip_ranges.append((old_low, low-1))

        # Skip [exclude_low, exclude_high]
        if compare_ips(low, exclude_high) < 0:
            if compare_ips(src_high, exclude_high) < 0:
                # exclusion completely overlaps the rest of the src range
                break
            else:
                src_entirely_excluded = False
                low = exclude_high

        # Capture (exclude_high, src_high]
        # if compare_ips(low, src_high) <= 0:
        # - hence we handle the `=` case via the `min()` function

        # `low+1` is addition on an IP Address; eg: 10.0.1.255 + 1 = 10.0.2.0
        ip_ranges.append((min(low+1, src_high), src_high))
        break
    # end while-loop

    src_after_excluded_cidrs = []
    for range in ip_ranges:
        src_after_excluded_cidrs += create_cidrs_from_ip_range(str(range[0]), str(range[1]))

    return src_after_excluded_cidrs, src_entirely_excluded

def main(src_cidrs, exclude_cidrs):
    if len(exclude_cidrs) == 0:
        return src_cidrs
    # if src_cidrs is empty, this will also return an empty list

    src_cidrs = sort_cidrs(src_cidrs)
    exclude_cidrs = sort_cidrs(exclude_cidrs)
    print(src_cidrs)
    print(exclude_cidrs)

    src_after_excluded_cidrs = []

    # O(n^2) double-traversal while-loop
    # TODO: don't start the range from 0; iteratively increment it
    # - would still technically be O(n^2) but average use-case would be better
    n = len(src_cidrs)
    m = len(exclude_cidrs)
    for i in range(n):
        t = len(src_after_excluded_cidrs)

        splits = []
        src_entirely_excluded = False
        for j in range(m):
            src_cidr = src_cidrs[i]
            exclude_cidr = exclude_cidrs[j]

            if compare_ips(get_cidr_last_addr(exclude_cidr), get_cidr_first_addr(src_cidr)) < 0:
                continue
            if compare_ips(get_cidr_last_addr(src_cidr), get_cidr_first_addr(exclude_cidr)) < 0:
                # exit the inner for-loop
                break
            # else, the CIDRs overlap

            split_cidrs, src_entirely_excluded = split_cidr_by_exclusion(src_cidr, exclude_cidr)
            splits += split_cidrs

            if src_entirely_excluded:
                # exit the inner for-loop
                break
        # end inner for-loop

        if (len(splits) == 0) and (not src_entirely_excluded):
            # CIDR wasn't split at all

            # TEMP:
            src_after_excluded_cidrs.append((str(get_cidr_first_addr(src_cidr)), str(get_cidr_last_addr(src_cidr))))
            #src_after_excluded_cidrs += src_cidr
        else:
            src_after_excluded_cidrs += splits
    # end outer for-loop

    print(src_after_excluded_cidrs)

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

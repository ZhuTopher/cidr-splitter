import ipaddress

# `ipaddress.IPv4Address::packed()` is a more succinct, way to get the
# binary representation of an IP address, but using the following
# functions from `socket` instead for forward-backward conversion clarity
from socket import inet_aton, inet_ntoa

# just including this in order to print Python bytes as raw hex characters
# (and not auto-encoded to ASCII/UTF characters)
from binascii import hexlify, unhexlify

from pprint import pprint

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

def create_cidrs_from_ip_range(low, high):
    low_ip = ipaddress.IPv4Address(low)
    high_ip = ipaddress.IPv4Address(high)
    # print('[ CIDR_FROM_RANGE ] low: %s' % low_ip)
    # print('[ CIDR_FROM_RANGE ] high: %s' % high_ip)

    # `ipaddress.summarize_address_range()` returns an iterator of
    # `IPv4Network`s in sorted (ascending) order
    cidrs = list(ipaddress.summarize_address_range(low_ip, high_ip))
    # print('[ CIDR_FROM_RANGE ] cidrs: %s' % cidrs)

    return cidrs

''' MAIN CODE '''

# NOTE: `ipaddress.IPv4Network::address_exclude()` is almost exactly
# what I need, except I also need to handle cases where the `exclude_cidr`
# isn't completely contained within the `src_cidr`
def split_cidr_by_exclusion(src_cidr, exclude_cidr):

    src_low = get_cidr_first_addr(src_cidr)
    src_high = get_cidr_last_addr(src_cidr)

    exclude_low = get_cidr_first_addr(exclude_cidr)
    exclude_high = get_cidr_last_addr(exclude_cidr)

    ip_ranges = []
    low = src_low

    # TODO: Handle edge cases more carefully (/32 CIDRs, exclusion superset src, etc.)
    # - currently including erroneous IPs
    # assumes src_low <= src_high and exclude_low <= exclude_high
    print('[ split_cidr_by_exclusion ] src_low: %s' % src_low)
    print('[ split_cidr_by_exclusion ] src_high: %s' % src_high)
    print('[ split_cidr_by_exclusion ] exclude_low: %s' % exclude_low)
    print('[ split_cidr_by_exclusion ] exclude_high: %s' % exclude_high)

    # one-pass CIDR splitting
    # - using `while` + `break` for control-flow (`goto` label behaviour)
    while True:
        # Not excluded [src_low, exclude_low)
        if compare_ips(low, exclude_low) < 0:
            if compare_ips(src_high, exclude_low) < 0:
                # exclusion doesn't intersect
                ip_ranges.append((src_low, src_high))
                break
            # else `compare_ips(src_high, exclude_low) >= 0`

            # `exclude_low-1` is subtraction on an IP Address; eg: 10.0.2.0 - 1 = 10.0.1.255
            # - safe due to `(src_)low < exclude_low`
            ip_ranges.append((low, exclude_low-1))
            low = exclude_low

        # Excluded [exclude_low, exclude_high]
         # - NOTE: `low` may still just be `src_low` if `src_low >= exclude_low`
        if compare_ips(low, exclude_high) <= 0:
            if compare_ips(src_high, exclude_high) <= 0:
                # exclusion completely overlaps the rest of the src range
                break
            # else `compare_ips(src_high, exclude_high) > 0`

            # `exclude_high+1` is addition on an IP Address; eg: 10.0.1.255 + 1 = 10.0.2.0`
            # - safe due to `src_high > exclude_high
            low = exclude_high+1

        # Not excluded (exclude_high, src_high]
        # - NOTE: `low` may still just be `src_low` if `src_low > exclude_high`
        ip_ranges.append((low, src_high))
        break
    # end while-loop

    sorted_split_cidrs = []
    for r in ip_ranges:
        sorted_split_cidrs += create_cidrs_from_ip_range(r[0], r[1])

    # returns an empty list only if the entire src_cidr was excluded, and
    # returns the original src_cidr range only if the src_cidr doesn't intersect the exclude_cidr
    return sorted_split_cidrs

def main(src_cidrs, exclude_cidrs):
    if len(exclude_cidrs) == 0:
        return src_cidrs  # if src_cidrs is empty, this will also return an empty list

    src_cidrs = sort_cidrs(src_cidrs)
    exclude_cidrs = sort_cidrs(exclude_cidrs)
    pprint(src_cidrs)
    pprint(exclude_cidrs)

    src_cidrs_after_exclude_cidrs = []

    # O(n^2) double-traversal while-loop
    n = len(src_cidrs)
    m = len(exclude_cidrs)
    for i in range(n):
        splits = []
        to_be_split = [src_cidrs[i]]

        # TODO: don't start the range from 0; increment it based on prior src_cidr's stopping points
        # - would still technically be O(n^2) but would remove pointless checks
        for j in range(m):
            if len(to_be_split) == 0:
                break

            src_cidr = to_be_split[0]
            exclude_cidr = exclude_cidrs[j]
            print('src: %s' % src_cidr)
            print('exclude: %s' % exclude_cidr)

            # if `src_cidr` doesn't overlap any (remaining) exclusions, we're done with this CIDR
            if compare_ips(get_cidr_last_addr(src_cidr), get_cidr_first_addr(exclude_cidr)) < 0:
                print('No further exclusions will intersect %s' % src_cidr)
                break  # any remaining CIDRs in `to_be_split` will be added outside this loop
            
            # if `exclude_cidr` doesn't overlap `src_cidr` and is below the first address of `src_cidr`,
            # then we can skip this and move on to the next exclusion
            if compare_ips(get_cidr_last_addr(exclude_cidr), get_cidr_first_addr(src_cidr)) < 0:
                continue

            # CIDRs overlap, so perform splitting
            sorted_split_cidrs = split_cidr_by_exclusion(src_cidr, exclude_cidr)
            to_be_split.pop(0)

            if len(sorted_split_cidrs) == 0:
                # then we excluded the entirety of the src_cidr
                print('Completely excluded %s' % src_cidr)
                continue  # might still have CIDRs in `to_be_split`

            print('src %s after exclusion %s:' % (src_cidr, exclude_cidr))
            continue_splitting = []
            for cidr in sorted_split_cidrs:
                print('\t%s' % cidr)
                if compare_ips(get_cidr_last_addr(cidr), get_cidr_first_addr(exclude_cidr)) < 0:
                    # this CIDR will never overlap any remaining exclusions
                    splits.append(cidr)
                else:
                    # this CIDR may overlap some remaining exclusions
                    continue_splitting.append(cidr)

            to_be_split = continue_splitting + to_be_split  # prepend to `to_be_split` to preserve order
        # end inner for-loop

        # add any remaining CIDRs which weren't analysed since the remaining exclusions wouldn't have intersected
        if len(to_be_split) > 0:
            splits += to_be_split
        src_cidrs_after_exclude_cidrs += splits
    # end outer for-loop

    return src_cidrs_after_exclude_cidrs

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
    src = [ipaddress.IPv4Network('192.168.2.0/24'),
           ipaddress.IPv4Network('172.16.5.1/32'),
           ipaddress.IPv4Network('10.0.14.0/23'),
           ipaddress.IPv4Network('10.0.16.0/23')]

    # exclude 192.168.2.0-192.168.2.1 -- exclusion trims front entries of src
    # exclude 10.0.16.0-10.0.16.255 -- src is superset of exclusion
    # exclude 10.0.17.0 -- have multiple exclusions for one src
    # exclude the entire 172.16.0.0 private IP range -- exclusion is superset of src
    exclude = [ipaddress.IPv4Network('192.168.2.0/31'),
               ipaddress.IPv4Network('10.0.16.0/24'),
               ipaddress.IPv4Network('10.0.17.0/32'),
               ipaddress.IPv4Network('172.16.0.0/12')]

    result = main(src, exclude)
    pprint(result)

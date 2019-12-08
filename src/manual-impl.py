import ipaddress

# `ipaddress.IPv4Address::packed()` is a more succinct, way to get the
# binary representation of an IP address, but using the following
# functions from `socket` instead for forward-backward conversion clarity
from socket import inet_aton, inet_ntoa

from binascii import hexlify, unhexlify

# this can be accomplished by `sorted(ipaddress.IPv4Network)` already,
# but this is for the purpose of exercise & translatability
def sort_cidrs(cidrs):
    packed_ip_cidrs = []
    for cidr in cidrs:
        packed_ip_cidrs.append(
           (inet_aton(str(get_cidr_first_addr(cidr))), cidr.prefixlen)
        )
    # double sort to use netmask as tie-breaker
    packed_ip_cidrs = sorted(packed_ip_cidrs, key=lambda x: x[1])
    packed_ip_cidrs = sorted(packed_ip_cidrs, key=lambda x: x[0])

    sorted_cidrs = []
    for cidr_pair in packed_ip_cidrs:
        sorted_cidrs.append(
            ipaddress.IPv4Network('%s/%d' % (inet_ntoa(cidr_pair[0]), cidr_pair[1]))
        )
    return sorted_cidrs

def get_cidr_first_addr(cidr):
    # Array-syntax is Python-specific, but the idea is just to get the first
    # address of the CIDR block

    # return cidr[0]
    return cidr.network_address

# - in translation, ensure integer types match the IP address type;
#   IPv4 needs 32-bit unsigned ints, IPv6 needs 128-bit unsigned ints
#   - need to fix bitmask lengths for this too
def get_cidr_last_addr(cidr):
    cidr_low_bytes = inet_aton(str(get_cidr_first_addr(cidr)))
    #print(inet_ntoa(cidr_low_bytes))
    #print(hexlify(cidr_low_bytes))

    # using bitwise addition to add hostmask to first address to find 'high'
    # - using bitwise AND with `0xffffffff` on summation to ensure 32-bit length
    #   - TODO: catch for overflow, and raise an error
    cidr_hostmask_bytes = inet_aton(str(cidr.hostmask))
    #print(inet_ntoa(cidr_hostmask_bytes))
    #print(hexlify(cidr_hostmask_bytes))
    
    cidr_high_bytes = int.from_bytes(cidr_low_bytes, byteorder='big', signed=False) + \
        int.from_bytes(cidr_hostmask_bytes, byteorder='big', signed=False)
    #print(cidr_high_bytes)
    cidr_high_bytes = cidr_high_bytes & 0xFFFFFFFF
    #print(cidr_high_bytes)
    cidr_high_bytes = int.to_bytes(cidr_high_bytes, length=4, byteorder='big', signed=False)
    #print(bytes(cidr_high_bytes))
    #print(inet_ntoa(cidr_high_bytes))
    #print(hexlify(cidr_high_bytes))

    return ipaddress.IPv4Address(inet_ntoa(cidr_high_bytes))

# - in translation, ensure integer types match the IP address type;
#   IPv4 needs 32-bit unsigned ints, IPv6 needs 128-bit unsigned ints
def compare_ips(ip_a, ip_b):
    a = int.from_bytes(inet_aton(str(ip_a)), byteorder='big', signed=False)
    b = int.from_bytes(inet_aton(str(ip_b)), byteorder='big', signed=False)

    if a < b:
        return -1
    if a > b:
        return 1
    return 0

# Given two IP address strings, `low` & `high`, create a (sorted) list of CIDR
# ranges (and individual IPs if necessary) which equate to that IP range
def create_cidrs_from_ip_range(low, high):
    print('[ create_cidrs_from_ip_range ] [ STUB ] (%s, %s)' % (low, high))
    return [(str(low), str(high))]

if __name__ == '__main__':
    print(sort_cidrs([
        ipaddress.IPv4Network('10.0.2.0/24'),
        ipaddress.IPv4Network('10.0.1.0/26'),
        ipaddress.IPv4Network('10.0.1.64/26'),
        ipaddress.IPv4Network('10.0.1.0/24'),
        ipaddress.IPv4Network('10.0.0.0/16')
    ]))

    print(get_cidr_first_addr(ipaddress.IPv4Network('10.0.4.0/22')))
    print(get_cidr_last_addr(ipaddress.IPv4Network('10.0.4.0/22')))

    print(compare_ips(ipaddress.IPv4Address('10.0.1.0'), ipaddress.IPv4Address('10.0.2.0')))
    print(compare_ips(ipaddress.IPv4Address('10.0.2.0'), ipaddress.IPv4Address('10.0.2.0')))
    print(compare_ips(ipaddress.IPv4Address('10.0.3.0'), ipaddress.IPv4Address('10.0.2.0')))

    print(create_cidrs_from_ip_range('10.0.0.0', '10.0.0.7'))

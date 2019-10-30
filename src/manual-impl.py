import ipaddress

from socket import inet_aton, inet_ntoa
from binascii import hexlify, unhexlify

# this can be accomplished by `sorted(ipaddress.ip_network)` already,
# but this is for the purpose of exercise & translatability
def sort_cidrs(cidrs):
    packed_ip_cidrs = []
    for cidr in cidrs:
        packed_ip_cidrs.append(
           (inet_aton(str(cidr[0])), cidr.prefixlen)
        )
    packed_ip_cidrs = sorted(packed_ip_cidrs, key=lambda x: x[0])

    sorted_cidrs = []
    for cidr_pair in packed_ip_cidrs:
        sorted_cidrs.append(
            ipaddress.ip_network('%s/%d' % (inet_ntoa(cidr_pair[0]), cidr_pair[1]))
        )
    return sorted_cidrs

def get_cidr_first_addr(cidr):
    # Array-syntax is Python-specific, but the idea is just to get the first
    # address of the CIDR block

    # return cidr[0]
    return cidr.network_address

def get_cidr_last_addr(cidr):
    cidr_low_bytes = get_cidr_first_addr(cidr)
    #print(inet_ntoa(cidr_low_bytes))
    #print(hexlify(cidr_low_bytes))

    # using bitwise addition to add hostmask to first address to find 'high'
    # - using bitwise AND with `0xffffffff` on summation to ensure 32-bit length
    #   - TODO: catch for overflow, and raise an error
    cidr_hostmask_bytes = inet_aton(str(cidr_cidr.hostmask))
    #print(inet_ntoa(cidr_hostmask_bytes))
    #print(hexlify(cidr_hostmask_bytes))
    
    cidr_high_bytes = int.from_bytes(cidr_low_bytes, byteorder='big', signed=False) + int.from_bytes(cidr_hostmask_bytes, byteorder='big', signed=False)
    #print(cidr_high_bytes)
    cidr_high_bytes = cidr_high_bytes & 0xFFFFFFFF
    #print(cidr_high_bytes)
    cidr_high_bytes = int.to_bytes(cidr_high_bytes, length=4, byteorder='big', signed=False)
    #print(bytes(cidr_high_bytes))
    #print(inet_ntoa(cidr_high_bytes))
    #print(hexlify(cidr_high_bytes))

    return ipaddress.ip_address(inet_ntoa(cidr_high_bytes))
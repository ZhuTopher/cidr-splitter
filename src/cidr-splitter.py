import ipaddress
from socket import inet_aton, inet_ntoa
from binascii import hexlify, unhexlify

'''
NOTE: ipaddress.ip_network.overlaps and ipaddress.ip_network.address_exclude
are pretty much exactly what I'm looking for; but I need to do this manually
since I want to convert this code to other languages (i.e: Java) which are
not as fortunate ;(
'''

def split_cidr_by_exclusion(src_cidr, exclude_cidr):
    # Array-syntax is Python-specific, but the idea is just to get the first
    # address of the CIDR block
    src_low = src_cidr[0]

    # TODO: use bit addition to add hostmask to first address to find 'high'
    # - this is more directly translatable between languages
    src_high = src_cidr[src_cidr.num_addresses-1]


# this can be accomplished by `sorted(ipaddress.ip_network)` already,
# but this is for the purpose of exercise & translatability
def sort_cidrs(cidrs):
    packed_ip_cidrs = []
    for cidr in cidrs:
        packed_ip_cidrs.append(
            # `cidr[0].packed` is more succinct, but using the following
            # approach instead for forward-backward conversion clarity
           (inet_aton(str(cidr[0])), cidr.prefixlen)
        )
    packed_ip_cidrs = sorted(packed_ip_cidrs, key=lambda x: x[0])

    sorted_cidrs = []
    for cidr_pair in packed_ip_cidrs:
        sorted_cidrs.append(
            ipaddress.ip_network('%s/%d' % (inet_ntoa(cidr_pair[0]), cidr_pair[1]))
        )
    return sorted_cidrs

def main(src_cidrs, exclude_cidrs):
    src_cidrs = sort_cidrs(src_cidrs)
    exclude_cidrs = sort_cidrs(exclude_cidrs)
    print(src_cidrs)
    print(exclude_cidrs)

    # double-traversal while-loops

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

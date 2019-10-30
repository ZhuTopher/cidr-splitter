# cidr-splitter

This is mostly just for practice but I also was unable to find a nice existing library which does this use-case.

I want to take a set of IPv4 CIDR ranges, and another set of IPv4 CIDR ranges to 'exclude' from those ranges.
The result would ideally be a list of IPv4 CIDR ranges which comprise the set subtraction of 'original \ exlusions'.

Furthermore I want this to be relatively 'light' so efficiency and memory matters; this is going to involve bit-wise operations.

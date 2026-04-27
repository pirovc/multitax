#!/usr/bin/env python3

from collections import Counter
from multitax import GtdbTx

representatives = False
vfrom = "214.1"
vto= "232"

gtdb_from = GtdbTx(version=vfrom)
gtdb_from.build_conversion(version=vto, representatives=representatives)
gtdb_to = GtdbTx(version=vto)
gtdb_to.build_lca()

table = {r: {} for r in gtdb_to._standard_ranks}

for r in gtdb_to._standard_ranks:
    tres = []
    # For all nodes of each standard rank
    for leaf in gtdb_from.nodes_rank(r):

        # Convert
        con: set[str] = gtdb_from.convert(leaf, version=vto)
        if con:
            lca = gtdb_to.lca(con)
        else:
            lca = "1" # missing
        
        # Get closest parent of the LCA node
        cr = gtdb_to.closest_parent(lca, ranks=gtdb_to._standard_ranks)
        tres.append(cr)
    
    # Get ranks of translations
    # None is the result of the LCA to the root node (since it is "no rank" and not in _standard_ranks)
    rank_counts = Counter(map(gtdb_to.rank, tres))
    for item, count in rank_counts.items():
        rank_counts[item] /= len(tres)
    table[r] = rank_counts

print(*["        missing"] + gtdb_to._standard_ranks, sep="\t")
for r1 in gtdb_to._standard_ranks:
    print(r1, end="\t")
    for r2 in [None] + gtdb_to._standard_ranks:
        print('{0:.2f}'.format(table[r1][r2]*100), end="\t")
    print()
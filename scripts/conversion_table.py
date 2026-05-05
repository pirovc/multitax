#!/usr/bin/env python3

from collections import Counter
from multitax import GtdbTx

representatives = False
vfrom = "226"
vto = "232"

gtdb_from = GtdbTx(version=vfrom)
gtdb_from.build_conversion(version=vto, representatives=representatives)
gtdb_to = GtdbTx(version=vto)
gtdb_to.build_lca()

table = {r: {} for r in gtdb_to._standard_ranks}
for r in gtdb_to._standard_ranks:
    tres = []
    missing = 0
    for leaf in gtdb_from.nodes_rank(r):
        con: set[str] = gtdb_from.convert(leaf, version=vto)
        if con:
            lca = gtdb_to.lca(con)
            cr = gtdb_to.rank(
                gtdb_to.closest_parent(lca, ranks=["root"] + gtdb_to._standard_ranks)
            )
        else:
            cr = "root"
            missing += 1
        tres.append(cr)

    rank_counts = Counter(tres)
    rank_counts["missing"] = missing
    rank_counts["root"] = rank_counts["root"] - missing

    for item, count in rank_counts.items():
        rank_counts[item] /= len(tres)
    table[r] = rank_counts

print(*["        missing", "root"] + gtdb_to._standard_ranks, sep="\t")
for r1 in gtdb_to._standard_ranks:
    print(r1, end="\t")
    for r2 in ["missing", "root"] + gtdb_to._standard_ranks:
        print("{0:.2f}".format(table[r1][r2] * 100), end="\t")
    print()

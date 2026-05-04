#!/usr/bin/env python3

from collections import Counter
from multitax import GtdbTx, NcbiTx

representatives = False
top_perc = None

gtdb_tax = GtdbTx(version="232")
gtdb_tax.build_lca()
ncbi_tax = NcbiTx(version="20250907", urls="https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/taxdump_20250907.tar.gz")
ncbi_tax.filter(["2", "2157"], desc=True) # Filter NCBI bacteria and archaea only to match GTDB

# Translation
ncbi_tax.build_translation(tax=gtdb_tax, representatives=representatives)

table = {r: {} for r in gtdb_tax._standard_ranks}
for r in gtdb_tax._standard_ranks:
    tres = []
    missing = 0
    # For all nodes of each standard rank
    for leaf in ncbi_tax.nodes_rank(r):
        tr = ncbi_tax.translate(leaf, top_perc=top_perc)
        if tr:
            lca = gtdb_tax.lca(tr)
            # Get closest parent of the LCA node on standard ranks, and then rank
            cr = gtdb_tax.rank(gtdb_tax.closest_parent(lca, ranks=["root"] + gtdb_tax._standard_ranks))
        else: # add as root, but keep track of missing translations
            cr = "root"
            missing += 1 
        tres.append(cr)

    # Count ranks, subtract missing from root
    rank_counts = Counter(tres)
    rank_counts["missing"] = missing
    rank_counts["root"] = rank_counts["root"] - missing

    # Percentage
    for item, count in rank_counts.items():
        rank_counts[item] /= len(tres)
    table[r] = rank_counts

print(*["        missing", "root"] + gtdb_tax._standard_ranks, sep="\t")
for r1 in gtdb_tax._standard_ranks:
    print(r1, end="\t")
    for r2 in ["missing", "root"] + gtdb_tax._standard_ranks:
        print('{0:.2f}'.format(table[r1][r2]*100), end="\t")
    print()
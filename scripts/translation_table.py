#!/usr/bin/env python3

from collections import Counter
from multitax import GtdbTx, NcbiTx

representatives = False
top_perc = 1

gtdb_tax = GtdbTx(version="232")
ncbi_tax = NcbiTx(urls="https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/taxdump_20250907.tar.gz")
# Filter NCBI bacteria and archaea only to speed-up LCA
ncbi_tax.filter(["2", "2157"], desc=True)
ncbi_tax.build_lca()

# Translation
gtdb_tax.build_translation(tax=ncbi_tax, representatives=representatives)

table = {r: {} for r in ncbi_tax._standard_ranks}

for r in ncbi_tax._standard_ranks:
    tres = []
    # For all nodes of each standard rank
    for leaf in gtdb_tax.nodes_rank(r):
        # Translate and apply LCA
        lca = ncbi_tax.lca(gtdb_tax.translate(leaf, top_perc=top_perc if top_perc else 1))
        
        # Get closest parent of the LCA node
        cr = ncbi_tax.closest_parent(lca, ranks=ncbi_tax._standard_ranks)
        tres.append(cr)
    
    # Get ranks of translations
    # None is the result of the LCA to the root node (since it is "no rank" and not in _standard_ranks)
    rank_counts = Counter(map(ncbi_tax.rank, tres))
    for item, count in rank_counts.items():
        rank_counts[item] /= len(tres)
    table[r] = rank_counts

print(*["        root"] + ncbi_tax._standard_ranks, sep="\t")
for r1 in ncbi_tax._standard_ranks:
    print(r1, end="\t")
    for r2 in [None] + ncbi_tax._standard_ranks:
        print('{0:.2f}'.format(table[r1][r2]*100), end="\t")
    print()
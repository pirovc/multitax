#!/usr/bin/env python3

import gzip
import sys
from pathlib import Path

if len(sys.argv) < 4:
    sys.exit('Usage: ./convert_gtdb_version.py ver_from ver_to taxa1 [taxa2 ...]\nExample: ./convert_gtdb_version.py 95 226 "s__Ruminococcus_A sp003011855" "s__Bact-08 sp003520315" "g__JOSHI-001"')

script_path = Path( __file__ ).parent.absolute()

ver_from = sys.argv[1]
ver_to = sys.argv[2]
taxa = sys.argv[3:]

data_from = {}
data_to = {}
with gzip.open(f"{script_path}/{ver_from}_acc_rep_lin_ncbi.tsv.gz", "rt") as file:
    for line in file:
        acc, rep, tax, _ = line.rstrip().split("\t")
        if rep == "t":
            for tx in tax.split(";"):
                if tx not in data_from:
                    data_from[tx] = []
                data_from[tx].append(acc)
with gzip.open(f"{script_path}/{ver_to}_acc_rep_lin_ncbi.tsv.gz", "rt") as file:
    for line in file:
        acc, _, tax, _ = line.rstrip().split("\t")
        data_to[acc] = tax

def lookup_taxa(lt):
    results = set()
    for acc in data_from[lt]:
        for tx in data_to.get(acc, "").split(";"):
            if tx.startswith(lt[:1]):
                results.add(tx)
    return results

for t in taxa:
    print(f"{ver_from}: {t} -> {ver_to}: {", ".join(lookup_taxa(t))}")
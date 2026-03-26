#!/usr/bin/env bash
set -euo pipefail

url_prefix="https://data.gtdb.ecogenomic.org/releases/"
# 80
curl "${url_prefix}/release80/80.0/bac_metadata_r80.tsv" | tail -n+2 | awk -F"\t" '{print $1"\t"$36"\t"$34"\t"$51}' | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 80_acc_rep_lin_ncbi.tsv.gz
# 83
curl "${url_prefix}/release83/83.0/bac_metadata_r83.tsv" | sed "s/\r//g" | tail -n+2 | awk -F"\t" '{print $1"\t"$34"\t"$93"\t"$52}' | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 83_acc_rep_lin_ncbi.tsv.gz
# 86.2
curl "${url_prefix}/release86/86.2/ar122_metadata_r86.2.tsv" | tail -n+2 | awk -F"\t" '{print $1"\t"$33"\t"$92"\t"$51}' | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 86.2_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release86/86.2/bac120_metadata_r86.2.tsv" | tail -n+2 | awk -F"\t" '{print $1"\t"$33"\t"$92"\t"$51}' | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 86.2_acc_rep_lin_ncbi.tsv.gz
# 89
curl "${url_prefix}/release89/89.0/ar122_metadata_r89.tsv" | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 89_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release89/89.0/bac120_metadata_r89.tsv" | tail -n+2 | cut -f 1,16,17,78  | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 89_acc_rep_lin_ncbi.tsv.gz
# 95
curl "${url_prefix}/release95/95.0/ar122_metadata_r95.tar.gz" | tar xzf - -O | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 95_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release95/95.0/bac120_metadata_r95.tar.gz" | tar xzf - -O | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 95_acc_rep_lin_ncbi.tsv.gz
# 202
curl "${url_prefix}/release202/202.0/ar122_metadata_r202.tar.gz" | tar xzf - -O | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 202_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release202/202.0/bac120_metadata_r202.tar.gz" | tar xzf - -O | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 202_acc_rep_lin_ncbi.tsv.gz
# 207
curl "${url_prefix}/release207/207.0/ar53_metadata_r207.tar.gz" | tar xzf - -O | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 207_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release207/207.0/bac120_metadata_r207.tar.gz" | tar xzf - -O | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 207_acc_rep_lin_ncbi.tsv.gz
# 214
curl "${url_prefix}/release214/214.1/ar53_metadata_r214.tsv.gz" | zcat | tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 214.1_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release214/214.1/bac120_metadata_r214.tsv.gz" | zcat |  tail -n+2 | cut -f 1,16,17,78 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 214.1_acc_rep_lin_ncbi.tsv.gz
# 220
curl "${url_prefix}/release220/220.0/ar53_metadata_r220.tsv.gz" | zcat | tail -n+2 | cut -f 1,19,20,81 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 220_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release220/220.0/bac120_metadata_r220.tsv.gz" | zcat | tail -n+2 | cut -f 1,19,20,81 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 220_acc_rep_lin_ncbi.tsv.gz
# 226
curl "${url_prefix}/release226/226.0/ar53_metadata_r226.tsv.gz" | zcat | tail -n+2 | cut -f 1,19,20,81  | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip > 226_acc_rep_lin_ncbi.tsv.gz
curl "${url_prefix}/release226/226.0/bac120_metadata_r226.tsv.gz" | zcat | tail -n+2 | cut -f 1,19,20,81 | sed 's/^[R|G][S|B]_GC[A|F]_\([0-9]*\).[0-9]*/G\1/' | gzip >> 226_acc_rep_lin_ncbi.tsv.gz

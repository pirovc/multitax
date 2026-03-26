## Files for taxa conversion and transalation

The files in this directory are a subset of metadata files from [GTDB](https://gtdb.ecogenomic.org) [downloads page](https://data.gtdb.ecogenomic.org/), with 4 columns: `accession <tab> gtdb_representative <tab> gtdb_taxonomy <tab> ncbi_taxid`

Example: 

```
G024295625	t	d__Bacteria;p__Bacillota;c__Bacilli;o__Lactobacillales;f__Streptococcaceae;g__Streptococcus;s__Streptococcus sp024295625	2963154
G002562265	f	d__Bacteria;p__Bacillota;c__Bacilli;o__Bacillales;f__Bacillaceae_G;g__Bacillus_A;s__Bacillus_A cereus	1396
```

Database and version numbers are removed from `accessions` as indicated by GTDB page: https://gtdb.ecogenomic.org/taxon-history

- `GB_GCA_000023565.1` -> `G000023565`
- `RS_GCF_000003135.1` -> `G000003135`

There are some differences between metadata columns and file types among versions. The script `make_acc_rep_lin.sh` can be used to download and generate the files.

Those files are used by MultiTax to transalate NCBI<->GTDB as well as convert GTDB versions.

To test the taxa conversion, you can use the script:

```
Usage: ./convert_gtdb_version.py FROM TO taxa1 [taxa2 ...]
Example: ./convert_gtdb_version.py 95 226 "s__Ruminococcus_A sp003011855" "s__Bact-08 sp003520315" "g__JOSHI-001"
```
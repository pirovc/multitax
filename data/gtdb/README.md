## GTDB auxiliary files

The `*_acc_rep_lin_ncbi.tsv.gz` files in this directory are a subset from metadata files from [GTDB](https://gtdb.ecogenomic.org) [downloads page](https://data.gtdb.ecogenomic.org/). They are used by MultiTax to transalate GTDB <-> NCBI and to convert GTDB taxa among versions.

One file for each released versions of GTDB was created with the name `{VERSION}_acc_rep_lin_ncbi.tsv.gz`, each containing 4 columns: `accession <tab> gtdb_representative <tab> gtdb_taxonomy <tab> ncbi_taxid`

Example: 

```
G024295625	t	d__Bacteria;p__Bacillota;c__Bacilli;o__Lactobacillales;f__Streptococcaceae;g__Streptococcus;s__Streptococcus sp024295625	2963154
G002562265	f	d__Bacteria;p__Bacillota;c__Bacilli;o__Bacillales;f__Bacillaceae_G;g__Bacillus_A;s__Bacillus_A cereus	1396
```

Database and version numbers are removed from `accessions` as indicated by [GTDB taxon history page](https://gtdb.ecogenomic.org/taxon-history):

- `GB_GCA_000023565.1` -> `G000023565`
- `RS_GCF_000003135.1` -> `G000003135`

There are some differences between metadata columns and file types among versions. To re-create the files, use the `make_acc_rep_lin_ncbi.sh`.

To test the taxa conversion, you can use the script `convert_gtdb_version.py`:

```sh
Usage: ./convert_gtdb_version.py FROM TO taxa1 [taxa2 ...]
Example: ./convert_gtdb_version.py 95 226 "s__Ruminococcus_A sp003011855" "s__Bact-08 sp003520315" "g__JOSHI-001"
```

Using the MultiTax package, the same can be achieved with:

```py
from multitax import GtdbTx
tax = GtdbTx(version="95")
tax.convert('s__Ruminococcus_A sp003011855', version="226")
tax.convert('s__Bact-08 sp003520315', version="226")
tax.convert('g__JOSHI-001', version="226")
```

More info about the conversion strategy: https://pirovc.github.io/multitax/multitax.html#GtdbTx.convert
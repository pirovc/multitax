# MultiTax [![GitHub release (latest by date)](https://img.shields.io/github/v/release/pirovc/multitax)](https://github.com/pirovc/multitax) [![Build Status](https://app.travis-ci.com/pirovc/multitax.svg?token=q6Nfx8pLHh8hV3hLz3Pq&branch=main)](https://app.travis-ci.com/pirovc/multitax) [![codecov](https://codecov.io/gh/pirovc/multitax/branch/main/graph/badge.svg)](https://codecov.io/gh/pirovc/multitax) [![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/multitax/README.html) [![install with pip](https://img.shields.io/badge/install%20with-pip-brightgreen.svg?style=flat)](https://pypi.org/project/multitax/)

A Python package for obtaining, parsing and exploring biological taxonomies.

## Description

MultiTax is a Python package that provides a standardised set of functions for downloading, parsing, filtering, exploring, translating, converting and writing multiple taxonomies, including GTDB, NCBI, Silva, Greengenes and Open Tree Taxonomy, as well as custom-formatted taxonomies. MultiTax main goals:

- to be fast, intuitive, generalised and easy to use.
- explore different taxonomies using the same set of commands.
- explore different versions of the same taxonomy.
- enable integration and compatibility with multiple taxonomies.
- convert nodes between same taxonomy versions.
- translate nodes between different taxonomies.

MultiTax handles taxonomic nodes. Sequence identifiers are not directly supported, but can be integrated with the `add()` function.

## Supported versions

- NCBI:
  - **current** (daily updated version)
  - custom with file/url for: `taxdump.tar.gz` or `nodes.dmp` (and optional `names.dmp` and `merged.dmp`). Older versions can be obtained [here](https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_archive/).
- GTDB:
  - 80, 83, 86.2, 89, 95, 202, 207, 214.1, 220, 226, **232**
  - custom with file/url
- Silva
  - lsu_138.2, **ssu_138.2**
  - custom with file/url
- Greengenes
  - 2022.10, **2024.09**
  - custom with file/url
- Ott
  - 3.6, **3.7.3**
  - custom with file/url
- Custom
  - custom with file/url with fields: `node`, `parent`, `rank`, `name`

Defaults to **version in bold**.

## Installation

### pip

```bash
pip install multitax
```

### conda

```bash
conda install -c bioconda multitax
```

### local

```bash
git clone https://github.com/pirovc/multitax.git
cd multitax
pip install .
```

## API Documentation

<https://pirovc.github.io/multitax/>

## Basic usage examples with GTDB

```python
>>> from multitax import GtdbTx

# Download and parse latest taxonomy version
>>> tax = GtdbTx()

# Get lineage for the Escherichia genus  
>>> tax.lineage("g__Escherichia")
['1', 'd__Bacteria', 'p__Pseudomonadota', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']
```

### Load

```python
>>> from multitax import GtdbTx  # or NcbiTx, SilvaTx, OttTx, GreengensTx
>>> tax = GtdbTx()

# Download and parse specific version
>>> tax = GtdbTx(version="220")

# Download and parse in memory AND write files to disk
>>> tax = GtdbTx(output_prefix="save/my/tax/files") 

# Download and parse in memory filtering only specific branch
>>> tax = GtdbTx(root_node="p__Proteobacteria") 

# Do not download, but parse local files
>>> tax = GtdbTx(files=["bac120_taxonomy.tsv.gz", "ar122_taxonomy.tsv.gz"])

# Show infos about loaded tax
>>> print(tax)
GtdbTx(version='220', source=['https://data.gtdb.ecogenomic.org/releases/release220/220.0/ar53_taxonomy_r220.tsv.gz', 'https://data.gtdb.ecogenomic.org/releases/release220/220.0/bac120_taxonomy_r220.tsv.gz'], datetime=datetime.datetime(2026, 3, 30, 10, 44, 52, 430845))
```

### Explore

```python
>>> from multitax import GtdbTx  # or NcbiTx, SilvaTx, OttTx, GreengensTx
>>> tax = GtdbTx()

# List parent node
>>> tax.parent("g__Escherichia")
'f__Enterobacteriaceae'

# List children nodes
>>> tax.children("g__Escherichia")
['s__Escherichia coli', 's__Escherichia albertii', 's__Escherichia fergusonii', 's__Escherichia marmotae', 's__Escherichia coli_F', 's__Escherichia ruysiae', 's__Escherichia sp005843885', 's__Escherichia whittamii', 's__Escherichia sp004211955', 's__Escherichia coli_E', 's__Escherichia sp002965065']

# Get parent node from a defined rank
>>> tax.parent_rank("s__Lentisphaera araneosa", "phylum")
'p__Verrucomicrobiota'

# Get the closest parent from a list of ranks
>>> tax.closest_parent("s__Lentisphaera araneosa", ranks=["phylum", "class", "family"])
'f__Lentisphaeraceae'

# Optional, pre-build lineages in memory for faster access
>>> tax.build_lineages()

# Get lineage
>>> tax.lineage("g__Escherichia")
['1', 'd__Bacteria', 'p__Pseudomonadota', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

# Get lineage of names
>>> tax.name_lineage("g__Escherichia")
['root', 'Bacteria', 'Pseudomonadota', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia']

# Get lineage of ranks
>>> tax.rank_lineage("g__Escherichia")
['root', 'domain', 'phylum', 'class', 'order', 'family', 'genus']

# Get lineage with defined ranks and root node
>>> tax.lineage("g__Escherichia", root_node="p__Pseudomonadota", ranks=["phylum", "class", "family", "genus"])
['p__Pseudomonadota', 'c__Gammaproteobacteria', 'f__Enterobacteriaceae', 'g__Escherichia']

# Get leaf nodes
>>> tax.leaves("g__Hadarchaeum")
['s__Hadarchaeum sp038871235', 's__Hadarchaeum sp038851515', 's__Hadarchaeum yellowstonense', 's__Hadarchaeum sp014361095']

# Search names and filter by rank
>>> tax.search_name("Luteolibacter muciniphilus", exact=False, rank="species")
['s__Luteolibacter muciniphilus_A', 's__Luteolibacter muciniphilus_B', 's__Luteolibacter muciniphilus_D', 's__Luteolibacter muciniphilus_E', 's__Luteolibacter muciniphilus_C']

# Show stats of loaded tax
>>> print(tax.stats())
{'leaves': 143614,
 'names': 181960,
 'nodes': 181960,
 'ranked_leaves': Counter({'species': 143614}),
 'ranked_nodes': Counter({'species': 143614,
                          'genus': 29405,
                          'family': 5932,
                          'order': 2164,
                          'class': 638,
                          'phylum': 204,
                          'domain': 2,
                          'root': 1}),
 'ranks': 181960}
```

### Filter

```python
>>> from multitax import GtdbTx  # or NcbiTx, SilvaTx, OttTx, GreengensTx
>>> tax = GtdbTx()

# Filter ancestors, keeping only nodes up-to "g__Escherichia" and "s__Pseudomonas aeruginosa"
>>> tax.filter(["g__Escherichia", "s__Pseudomonas aeruginosa"])
>>> print(tax.stats())
{'leaves': 2,
 'names': 11,
 'nodes': 11,
 'ranked_leaves': Counter({'species': 1, 'genus': 1}),
 'ranked_nodes': Counter({'genus': 2,
                          'family': 2,
                          'order': 2,
                          'class': 1,
                          'phylum': 1,
                          'domain': 1,
                          'species': 1,
                          'root': 1}),
 'ranks': 11}

# Filter descendants, keeping only children nodes from "d__Archaea"
>>> tax = GtdbTx()
>>> tax.filter(["d__Archaea"], desc=True)
>>> print(tax.stats())
{'leaves': 6968,
 'names': 9910,
 'nodes': 9910,
 'ranked_leaves': Counter({'species': 6968}),
 'ranked_nodes': Counter({'species': 6968,
                          'genus': 2079,
                          'family': 603,
                          'order': 172,
                          'class': 65,
                          'phylum': 21,
                          'domain': 1,
                          'root': 1}),
 'ranks': 9910}
```

### Add, remove, prune

```python
>>> from multitax import GtdbTx  # or NcbiTx, SilvaTx, OttTx, GreengensTx
>>> tax = GtdbTx()

# Add node to the tree
>>> tax.add("my_custom_node", "g__Escherichia", name="my custom name", rank="strain")
>>> tax.lineage("my_custom_node")
['1', 'd__Bacteria', 'p__Pseudomonadota', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia', 'my_custom_node']

# Remove node from tree (warning: removing parent nodes may break tree -> use check_consistency)
>>> tax.remove("s__Pseudomonas aeruginosa", check_consistency=True)

# Prune (remove) full branches of the tree under a certain node
>>> tax.prune("g__Escherichia")
```

### LCA (lowest common ancestor)

```python
>>> from multitax import GtdbTx
>>> tax = GtdbTx()
>>> tax.build_lca()
>>> tax.lca(["g__Escherichia", "s__Pseudomonas aeruginosa"])
'c__Gammaproteobacteria'
```

### Translate

```python
>>> from multitax import GtdbTx, NcbiTx
>>> ncbi_tax = NcbiTx()
>>> gtdb_tax = GtdbTx()

# Build translation
>>> gtdb_tax.build_translation(ncbi_tax)

# GTDB -> NCBI
>>> gtdb_tax.translate("s__Luteolibacter muciniphilus_A")
{'239935', '2562705'}

# Get a one-to-one translation using the lowest common ancestor
>>> ncbi_tax.filter(["2", "2157"], desc=True)  # Optional, keep only Bacteria and Archaea to reduce LCA build time
>>> ncbi_tax.build_lca()  # Optional, runs on the first .lca() call
>>> ncbi_tax.lca(gtdb_tax.translate("s__Luteolibacter muciniphilus_A"))
'1647988'

# NCBI -> GTDB
# Build translation
>>> ncbi_tax.build_translation(gtdb_tax)
>>> ncbi_tax.translate('620')
{'g__Serratia', 'g__Escherichia', 'g__Proteus'}
>>> gtdb_tax.lca(ncbi_tax.translate('620'))
'f__Enterobacteriaceae'
```

### Convert between GTDB versions

```python
>>> from multitax import GtdbTx
# Taxa from version 95 to version 226, based on representative genomes
>>> tax = GtdbTx(version="95")
>>> tax.convert("g__OLB14", version="226")
{'g__Villigracilis'}
```

### Write

```python
# Write tax to file
>>> tax.write("custom_tax.tsv", cols=["node", "rank", "name_lineage"])
```

custom_tax.tsv:

```txt
g__Escherichia             genus    root|Bacteria|Proteobacteria|Gammaproteobacteria|Ent#erobacterales|Enterobacteriaceae|Escherichia
f__Enterobacteriaceae      family   root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales|Enterobacteriaceae
o__Enterobacterales        order    root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales
c__Gammaproteobacteria     class    root|Bacteria|Proteobacteria|Gammaproteobacteria
...
```

### Other taxonomies can be used similarly

```python
# NCBI
>>> from multitax import NcbiTx
>>> tax = NcbiTx()
>>> tax.lineage("561")    
['1', '131567', '2', '3379134', '1224', '1236', '91347', '543', '561']

# Silva
>>> from multitax import SilvaTx
>>> tax = SilvaTx()
>>> tax.lineage("46463")    
['1', '3', '2375', '3303', '46449', '46454', '46463']

# Open Tree taxonomy
>>> from multitax import OttTx
>>> tax = OttTx()
>>> tax.lineage("474503")
['805080', '93302', '844192', '248067', '822744', '768012', '424023', '474503']

# GreenGenes
>>> from multitax import GreengenesTx
>>> tax = GreengenesTx()
>>> tax.lineage("f__Enterobacteriaceae_A_725029")
['1', 'd__Bacteria', 'p__Pseudomonadota', 'c__Gammaproteobacteria', 'o__Enterobacterales_737866', 'f__Enterobacteriaceae_A_725029']
```

## Details

- After downloading and parsing the desired taxonomies, MultiTax works fully offline.
- Taxonomies are parsed into `nodes`. Each node is annotated with a `name` and a `rank`.
- Some taxonomies have a numeric taxonomic identifier (e.g. NCBI), while others use the rank and name as an identifier (e.g. GTDB). In MultiTax, all identifiers are treated as strings.
- A single root node is defined by default for each taxonomy (or `1` when not defined). This can be changed using the `root_node` parameter when loading the taxonomy, as well as the `root_parent`, `root_name` and `root_rank` parameters. If the `root_node` already exists, the tree will be filtered.
- Standard values for unknown or undefined nodes can be configured using the `undefined_node`, `undefined_name` and `undefined_rank` parameters. These are the default values returned when nodes, names or ranks are not found.
- Taxonomy files are automatically downloaded or can be loaded from disk using the `files` parameter. Alternative `urls` can be provided. When downloaded, files are handled in memory. It is possible to save the downloaded file to disk using the `output_prefix`.

## Translation between taxonomies

Currently, only NCBI and GTDB have a translation implemented. There is no 1-to-1 translation between GTDB-NCBI because they are based on different concepts. Since GTDB uses a sub-set of NCBI genomes (bacterial and archaeal genomes only), it is possible to "translate" nodes among those taxonomies. Below you find a compatibility table between standard ranks for all GTDB genomes (R232) against the NCBI taxonomy:

```txt
        root    domain  phylum  class   order   family  genus   species
domain  100.00  0.00    0.00    0.00    0.00    0.00    0.00    0.00
phylum  18.27   74.11   7.61    0.00    0.00    0.00    0.00    0.00
class   10.54   64.03   20.16   5.27    0.00    0.00    0.00    0.00
order   5.06    47.94   25.56   15.91   5.53    0.00    0.00    0.00
family  2.71    39.77   29.38   13.98   9.68    4.49    0.00    0.00
genus   0.70    20.53   29.70   16.53   12.54   12.84   7.15    0.00
species 0.13    3.16    3.66    2.73    2.14    2.41    5.07    80.70
```

Besides at species level (80.70%), the 1-to-1 rank translation rates are very low, e.g. only 7.15% of genus nodes from GTDB translate to a unique genus on NCBI. The higher level values are achieved by applying the `lca()` method for the translated nodes and using the closest standard rank, script available: `scripts/translation_table_gtdb-ncbi.py`.

The translation can be tweaked to use the majority of tranalated nodes with the `top_perc` parameter in the `translate()` method. This is useful to get better resolution in the translated nodes by ignoring minor differences. For example, using `top_perc=0.95`:

```txt
        root    domain  phylum  class   order   family  genus   species
domain  0.00    100.00  0.00    0.00    0.00    0.00    0.00    0.00
phylum  2.03    80.20   17.77   0.00    0.00    0.00    0.00    0.00
class   1.55    61.71   29.30   7.44    0.00    0.00    0.00    0.00
order   0.81    43.39   31.01   18.03   6.76    0.00    0.00    0.00
family  0.64    36.05   32.19   15.18   10.45   5.50    0.00    0.00
genus   0.37    19.21   29.69   16.92   12.73   13.17   7.91    0.00
species 0.11    3.07    3.63    2.71    2.12    2.39    5.03    80.94
```

Alternatively, the translation can be also based solely on GTDB representatives (ith `representatives=True` param in `build_translation()` method. The conversion table in this scenario give an 1-to-1 species translation:

```txt
        root    domain  phylum  class   order   family  genus   species
domain  100.00  0.00    0.00    0.00    0.00    0.00    0.00    0.00
phylum  15.23   75.13   9.64    0.00    0.00    0.00    0.00    0.00
class   7.13    65.89   21.24   5.74    0.00    0.00    0.00    0.00
order   2.72    47.21   27.05   16.59   6.42    0.00    0.00    0.00
family  1.10    37.88   30.40   14.82   10.37   5.42    0.00    0.00
genus   0.24    17.79   29.42   17.12   13.13   13.68   8.63    0.00
species 0.00    0.00    0.00    0.00    0.00    0.00    0.00    100.00
```

Use `representatives` and/or `top_perc` with caution, since they may result in an "approximate" translation.

The translation from NCBI considering only archaeal and bacterial taxa to GTDB (R232):

```txt
        missing root    domain  phylum  class   order   family  genus   species
domain  0.00    100.00  0.00    0.00    0.00    0.00    0.00    0.00    0.00
phylum  6.90    14.22   31.03   47.84   0.00    0.00    0.00    0.00    0.00
class   8.70    13.83   32.41   7.91    37.15   0.00    0.00    0.00    0.00
order   8.92    9.48    24.54   4.28    9.85    42.94   0.00    0.00    0.00
family  9.14    4.74    20.14   3.81    6.18    10.91   45.09   0.00    0.00
genus   13.74   1.11    6.81    1.44    2.81    2.79    16.82   54.48   0.00
species 82.80   0.03    0.20    0.05    0.09    0.11    0.31    0.82    15.58
```

note that the translation from GTDB to NCBI is only partially possible and it is based on the genomes included in the GTDB release, therefore the `missing` column. Script available: `scripts/translation_table_ncbi-gtdb.py`

### Current status and possible translations

 |from/to |NCBI     |GTDB     |SILVA    |OTT      |GG       |
 |--------|---------|---------|---------|---------|---------|
 |NCBI    |-        |PART     |*[part]* |*[part]* |no       |
 |GTDB    |FULL     |-        |*[part]* |no       |*[part]* |
 |SILVA   |*[full]* |*[part]* |-        |*[part]* |no       |
 |OTT     |*[part]* |no       |*[part]* |-        |no       |
 |GG      |no       |*[part]* |no       |no       |-        |

Legend:

- FULL: complete translation available
- PART: partial translation available
- no: no translation possible
- *[full]*/*[part]*: not yet implemented

## Similar projects

- <https://github.com/FOI-Bioinformatics/flextaxd>
- <https://github.com/shenwei356/taxonkit>
- <https://github.com/bioforensics/pytaxonkit>
- <https://github.com/chanzuckerberg/taxoniq>
- <https://github.com/sherrillmix/taxonomiz>
- <https://github.com/etetoolkit/ete>
- <https://github.com/apcamargo/taxopy>

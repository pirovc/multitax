# MultiTax  [![Build Status](https://travis-ci.org/pirovc/multitax.svg?branch=main)](https://travis-ci.org/pirovc/multitax) [![codecov](https://codecov.io/gh/pirovc/multitax/branch/main/graph/badge.svg)](https://codecov.io/gh/pirovc/multitax) [![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/multitax/README.html)

Python package to obtain, parse and explore biological taxonomies

## Description

MultiTax is a Python package that provides a common and generalized set of functions to download, parse, filter and explore multiple biological taxonomies (**GTDB, NCBI, Silva, Greengenes, Open Tree taxonomy**) and custom formatted taxonomies. Main goals are:

 - Be fast, intuitive, generalized and easy to use
 - Explore different taxonomies with same set of commands
 - Enable integration and compatibility with multiple taxonomies
 - Translate taxonomies (partially implemented)
 - Convert taxonomies (not yet implemented)

MultiTax does not link sequence identifiers to taxonomic nodes, it just handles the taxonomy alone. Some kind of integration to work with sequence ids is planned, but not yet implemented.

## API Documentation

https://pirovc.github.io/multitax/

## Installation

### pip

	pip install multitax

### conda

	conda install -c bioconda multitax

### local

```bash
git clone https://github.com/pirovc/multitax.git
cd multitax
python setup.py install --record files.txt
```

## Basic Example with GTDB

```python
from multitax import GtdbTx

# Download and parse taxonomy
tax = GtdbTx()

# Get lineage for the Escherichia genus  
tax.lineage("g__Escherichia")
# ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']
```

## Further Examples

 - [List of functions](https://pirovc.github.io/multitax/multitax/multitax.html)

### Obtain/load/parse taxonomy

```python
from multitax import GtdbTx  # or NcbiTx, SilvaTx, ...

# Download and parse in memory
tax = GtdbTx()

# Parse local files
tax = GtdbTx(files=["bac120_taxonomy.tsv.gz", "ar122_taxonomy.tsv.gz"])

# Download, write and parse files
tax = GtdbTx(output_prefix="my/path/") 

# Download and filter only specific branch
tax = GtdbTx(root_node="p__Proteobacteria") 
```

### Explore

```python
# List parent node
tax.parent("g__Escherichia")
# f__Enterobacteriaceae

# List children nodes
tax.children("g__Escherichia")
# ['s__Escherichia flexneri', 's__Escherichia coli', 's__Escherichia dysenteriae', 's__Escherichia coli_D', 's__Escherichia albertii', 's__Escherichia marmotae', 's__Escherichia coli_C', 's__Escherichia sp005843885', 's__Escherichia sp000208585', 's__Escherichia fergusonii', 's__Escherichia sp001660175', 's__Escherichia sp004211955', 's__Escherichia sp002965065']

# Get parent node from a defined rank
tax.parent_rank("s__Lentisphaera araneosa", "phylum")
# 'p__Verrucomicrobiota'

# Get the closest parent from a list of ranks
tax.closest_parent("s__Lentisphaera araneosa", ranks=["phylum", "class", "family"])
# 'f__Lentisphaeraceae'

# Get lineage
tax.lineage("g__Escherichia")
# ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

# Get lineage of names
tax.name_lineage("g__Escherichia")
# ['root', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia']

# Get lineage of ranks
tax.rank_lineage("g__Escherichia")
# ['root', 'domain', 'phylum', 'class', 'order', 'family', 'genus']

# Get lineage with defined ranks and root node
tax.lineage("g__Escherichia", root_node="p__Proteobacteria", ranks=["phylum", "class", "family", "genus"])
# ['p__Proteobacteria', 'c__Gammaproteobacteria', 'f__Enterobacteriaceae', 'g__Escherichia']

# Build lineages in memory for faster access
tax.build_lineages()

# Get leaf nodes
tax.leaves("p__Hadarchaeota")
# ['s__DG-33 sp004375695', 's__DG-33 sp001515185', 's__Hadarchaeum yellowstonense', 's__B75-G9 sp003661465', 's__WYZ-LMO6 sp004347925', 's__B88-G9 sp003660555']

# Search names and filter by rank
tax.search_name("Escherichia", exact=False, rank="genus")
# ['g__Escherichia', 'g__Escherichia_C']

# Show stats of loaded tax
tax.stats()
#{'leaves': 31910,
# 'names': 45503,
# 'nodes': 45503,
# 'ranked_leaves': Counter({'species': 31910}),
# 'ranked_nodes': Counter({'species': 31910,
#                          'genus': 9428,
#                          'family': 2600,
#                          'order': 1034,
#                          'class': 379,
#                          'phylum': 149,
#                          'domain': 2,
#                          'root': 1}),
# 'ranks': 45503}

# Filter ancestors (desc=True for descendants)
tax.filter(['g__Escherichia', 's__Pseudomonas aeruginosa'])
tax.stats()
#{'leaves': 2,
# 'names': 11,
# 'nodes': 11,
# 'ranked_leaves': Counter({'genus': 1, 'species': 1}),
# 'ranked_nodes': Counter({'genus': 2,
#                          'family': 2,
#                          'order': 2,
#                          'class': 1,
#                          'phylum': 1,
#                          'domain': 1,
#                          'species': 1,
#                          'root': 1}),
# 'ranks': 11}

# Write tax to file
tax.write("custom_tax.tsv", cols=["node", "rank", "name_lineage"])

#g__Escherichia             genus    root|Bacteria|Proteobacteria|Gammaproteobacteria|Ent#erobacterales|Enterobacteriaceae|Escherichia
#f__Enterobacteriaceae      family   root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales|Enterobacteriaceae
#o__Enterobacterales        order    root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales
#c__Gammaproteobacteria     class    root|Bacteria|Proteobacteria|Gammaproteobacteria
#...
```

### Translating

```python
# NCBI
from multitax import GtdbTx, NcbiTx
ncbi_tax = NcbiTx()
gtdb_tax = GtdbTx()
gtdb_tax.build_translation(ncbi_tax)
gtdb_tax.translate("g__Escherichia")
# {'1301', '547', '561', '570', '590', '620'}
```

### The same applies to the other taxonomies

```python
# NCBI
from multitax import NcbiTx
tax = NcbiTx()
tax.lineage("561")    
# ['1', '131567', '2', '1224', '1236', '91347', '543', '561']

# Silva
from multitax import SilvaTx
tax = SilvaTx()
tax.lineage("46463")    
# ['1', '3', '2375', '3303', '46449', '46454', '46463']

# Open Tree taxonomy
from multitax import OttTx
tax = OttTx()
tax.lineage("474503")
# ['805080', '93302', '844192', '248067', '822744', '768012', '424023', '474503']

# GreenGenes
from multitax import GreengenesTx
tax = GreengenesTx()
tax.lineage("f__Enterobacteriaceae")
# ['1', 'k__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacteriales', 'f__Enterobacteriaceae']
```

## LCA integration

Using pylca: https://github.com/pirovc/pylca

    conda install -c bioconda pylca

```python
from pylca.pylca import LCA
from multitax import GtdbTx

# Download and parse GTDB Taxonomy
tax = GtdbTx()

# Build LCA structure
L = LCA(tax._nodes)

# Get LCA
L("s__Escherichia dysenteriae", "s__Pseudomonas aeruginosa")
# 'c__Gammaproteobacteria'
```

## General information
 
 - Taxonomies are parsed into `nodes`. Each node is annotated with a `name` and a `rank`.
 - Some taxonomies have a numeric taxonomic identifier (e.g. NCBI) and other use the rank + name as an identifier (e.g. GTDB). In MultiTax all identifiers are treated as strings.
 - A single root node is defined by default for each taxonomy (or `1` when not defined). This can be changed with `root_node` when loading the taxonomy (as well as annotations `root_parent`, `root_name`, `root_rank`). If the `root_node` already exists, the tree will be filtered.
 - Standard values for unknown/undefined nodes can be configured with `undefined_node`,`undefined_name` and `undefined_rank`. Those are default values returned when nodes/names/ranks are not found.
 - Taxonomy files are automatically downloaded or can be loaded from disk (`files` parameter). Alternative `urls` can be provided. When downloaded, files are handled in memory. It is possible to save the downloaded file to disk with `output_prefix`.

## Translation between taxonomies

Partially implemented. The goal is to map different taxonomies if the linkage data is available. That's what is currently availble.


 |from/to |NCBI     |GTDB   |SILVA     |OTT     |GG    |
 |--------|---------|-------|----------|--------|------|
 |NCBI    |-        |PART   |[part]    |[part]  |no    |
 |GTDB    |FULL     |-      |[part]    |no      |[part]|
 |SILVA   |[full]   |[part] |-         |[part]  |no    |
 |OTT     |[part]   |no     |[part]    |-       |no    |
 |GG      |no       |[part] |no        |no      |-     |

Legend:

 - full: complete translation available
 - part: partial translation available
 - no: no translation possible
 - []: not yet implemented

### Files and information about specific translations

 - NCBI <-> GTDB
   - GTDB is a subset of the NCBI repository, so the translation from NCBI to GTDB can be only partial
   - Translation in both ways is based on: https://data.gtdb.ecogenomic.org/releases/latest/ar53_metadata.tar.gz and https://data.gtdb.ecogenomic.org/releases/latest/bac120_metadata.tar.gz

## Further ideas

- Add/remove/update nodes
- Conversion between taxonomies (write on specific format)

## Similar projects

- https://github.com/FOI-Bioinformatics/flextaxd
- https://github.com/shenwei356/taxonkit
- https://github.com/bioforensics/pytaxonkit
- https://github.com/chanzuckerberg/taxoniq
- https://github.com/sherrillmix/taxonomizr

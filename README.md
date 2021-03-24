# MultiTax

Pyhton library that provides a common interface to obtain, parse and interact with biological taxonomies (GTDB, NCBI, Silva, Greengenes, Open Tree taxonomy) + "Custom" and "Empty" taxonomies. 

## Goals
 
 - Common interface to work with different taxonomies
 - Fast, intuitive, generalized and easy to use
 - Enable integration and compatibility with multiple taxonomies without any effort
 - Translation between taxonomies (not yet implemented)

## Installation

    python setup.py install --record files.txt

## Basic Example with GTDB

    from multitax import GtdbTx
    
    # Download taxonomy
    tax = GtdbTx()

    # Get lineage for the Escherichia genus  
    tax.lineage("g__Escherichia")
    # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

## Further Usage

    from multitax import GtdbTx
    
    # Parse local files
    tax = GtdbTx(files=["bac120_taxonomy.tsv.gz", "ar122_taxonomy.tsv.gz"])
    # Download, write and parse files
    tax = GtdbTx(output_prefix="my/path/") 

    tax.parent("g__Escherichia")
    # f__Enterobacteriaceae
    
    tax.children("g__Escherichia")
    # ['s__Escherichia flexneri', 's__Escherichia coli', 's__Escherichia dysenteriae', 's__Escherichia coli_D', 's__Escherichia albertii', 's__Escherichia marmotae', 's__Escherichia coli_C', 's__Escherichia sp005843885', 's__Escherichia sp000208585', 's__Escherichia fergusonii', 's__Escherichia sp001660175', 's__Escherichia sp004211955', 's__Escherichia sp002965065']

    tax.node(name="Escherichia")
    # ['g__Escherichia']

    tax.rank("g__Escherichia")
    # 'genus'

    tax.parent_rank("s__Lentisphaera araneosa", "phylum")
    # 'p__Verrucomicrobiota'

    tax.lineage("g__Escherichia")
    # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

    tax.name_lineage("g__Escherichia")
    # ['root', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia']

    tax.rank_lineage("g__Escherichia")
    # ['root', 'domain', 'phylum', 'class', 'order', 'family', 'genus']

    tax.lineage("g__Escherichia", ranks=["class", "family", "genus"])
    # ['c__Gammaproteobacteria', 'f__Enterobacteriaceae', 'g__Escherichia']

    tax.lineage("g__Escherichia", root_node="p__Proteobacteria")
    # ['p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

    tax.leaves("p__Hadarchaeota")
    # ['s__DG-33 sp004375695', 's__DG-33 sp001515185', 's__Hadarchaeum yellowstonense', 's__B75-G9 sp003661465', 's__WYZ-LMO6 sp004347925', 's__B88-G9 sp003660555']

    tax.stats()
    # {'nodes': 45503, 'ranks': 45503, 'names': 45503, 'unique_ranks': 8, ('nodes', 'class'): 379, ('nodes', 'domain'): 2, ('nodes', 'species'): 31910, ('nodes', 'order'): 1034, ('nodes', 'genus'): 9428, ('nodes', 'root'): 1, ('nodes', 'phylum'): 149, ('nodes', 'family'): 2600}

    tax.filter(['g__Escherichia', 's__Pseudomonas aeruginosa'])
    # Keep only lineage of ancestors (desc=True to keep only lineage of descendants)
    
    tax.stats()
    # {'nodes': 11, 'ranks': 11, 'names': 11, 'unique_ranks': 8, ('nodes', 'species'): 1, ('nodes', 'phylum'): 1, ('nodes', 'family'): 2, ('nodes', 'domain'): 1, ('nodes', 'root'): 1, ('nodes', 'class'): 1, ('nodes', 'genus'): 2, ('nodes', 'order'): 2}

    tax.write("custom_tax.tsv", cols=["node", "rank", "name_lineage"])

    g__Escherichia             genus    root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales|Enterobacteriaceae|Escherichia
    f__Enterobacteriaceae      family   root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales|Enterobacteriaceae
    o__Enterobacterales        order    root|Bacteria|Proteobacteria|Gammaproteobacteria|Enterobacterales
    c__Gammaproteobacteria     class    root|Bacteria|Proteobacteria|Gammaproteobacteria
    ...
    
    tax.build_lineages()
    # pre-build lineages in memory

    tax.check_consistency()
    # check if taxonomy tree is valid
    
    #
    # The same goes for the other taxonomies
    #

    # NCBI
    from multitax import NcbiTx
    tax = NcbiTx(files="taxdump.tar.gz")
    tax.lineage("561")    
    # ['1', '131567', '2', '1224', '1236', '91347', '543', '561']

    # Silva
    from multitax import SilvaTx
    tax = SilvaTx(files="tax_slv_ssu_138.1.txt.gz")
    tax.lineage("46463")    
    # ['1', '3', '2375', '3303', '46449', '46454', '46463']

    # Open Tree taxonomy
    from multitax import OttTx
    tax = OttTx(files="ott3.2.tgz")
    tax.lineage("474503")
    # ['805080', '93302', '844192', '248067', '822744', '768012', '424023', '474503']

    # GreenGenes
    from multitax import GreengenesTx
    tax = GreengenesTx(files="gg_13_5_taxonomy.txt.gz")
    tax.lineage("f__Enterobacteriaceae")
    # ['1', 'k__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacteriales', 'f__Enterobacteriaceae']

## General information

 - Taxonomies are parsed into nodes. Each node can be annotated with a name and a rank.
 - A single root node is defined by default. This node can be changed `root_node` as well as its annotations `root_parent`, `root_name`, `root_rank`.
 - Standard values for unknown/undefined nodes can be configured (`unknown_node`,`unknown_name`, `unknown_rank`). Those are default values returned when nodes/names/ranks are not found.
 - Files can be loaded from disk `files` or are automatically downloaded. Alternative `urls` can be provided. When downloaded, files are handled in memory. It is possible to dump the downloaded file to disk with `output_prefix`.

## LCA integration

Using pylca: https://github.com/pirovc/pylca

    from pylca.pylca import LCA
    from multitax import GtdbTx

    tax = GtdbTx()
    L = LCA(tax._nodes)

    L("s__Escherichia dysenteriae", "s__Pseudomonas aeruginosa")
    # 'c__Gammaproteobacteria'
    
## Translation between taxonomies

Not yet implemented. The goal here is to map different taxonomies if the linkage data is available. That's what I think it will be possible.

 |from/to |NCBI   |GTDB   |SILVA   |OTT   |GG  |
 |--------|-------|-------|--------|------|----|
 |NCBI    |-      |part   |part    |part  |no  |
 |GTDB    |full   |-      |no      |no    |no  |
 |SILVA   |full   |no     |-       |part  |no  |
 |OTT     |part   |no     |part    |-     |no  |
 |GG      |no     |no     |no      |no    |-   |


## TODO list

- unit tests
- integration tests
- CustomTx
- DummyTx
- better stats
- translate
- release

## Similar projects

- https://github.com/FOI-Bioinformatics/flextaxd
- https://github.com/shenwei356/taxonkit
- https://github.com/bioforensics/pytaxonkit
- https://github.com/chanzuckerberg/taxoniq

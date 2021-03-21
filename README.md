# MultiTax

Pyhton library that provides a common interface to obtain, parse and interact with biological taxonomies (GTDB, NCBI, Silva, Greengenes, Open Tree taxonomy) + "Custom" and "Empty" taxonomies. 

## Goals
 
 - Fast, intuitive, generalied and easy to use
 - Enable tools and scripts to easily extend compatibility with multiple taxonomies without any effort

## Installation

    python setup.py install --record files.txt

## Basic Example with GTDB

    from multitax.gtdbtx import GtdbTx
    
    # Download taxonomy
    tax = GtdbTx()

    # Get lineage for the Escherichia genus  
    tax.get_lineage("g__Escherichia")
    # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

## Further Usage

    from multitax.gtdbtx import GtdbTx
    
    # Parse local files
    tax = GtdbTx(files=["bac120_taxonomy.tsv.gz", "ar122_taxonomy.tsv.gz"])
    # Download, write and parse files
    tax = GtdbTx(output_prefix="my/path/") 

    tax.get_parent("g__Escherichia")
    # f__Enterobacteriaceae
    
    tax.get_children("g__Escherichia")
    # ['s__Escherichia flexneri', 's__Escherichia coli', 's__Escherichia dysenteriae', 's__Escherichia coli_D', 's__Escherichia albertii', 's__Escherichia marmotae', 's__Escherichia coli_C', 's__Escherichia sp005843885', 's__Escherichia sp000208585', 's__Escherichia fergusonii', 's__Escherichia sp001660175', 's__Escherichia sp004211955', 's__Escherichia sp002965065']

    tax.get_node(name="Escherichia")
    # ['g__Escherichia']

    tax.get_rank("g__Escherichia")
    # 'genus'

    tax.get_lineage("g__Escherichia")
    # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

    tax.get_name_lineage("g__Escherichia")
    # ['root', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia']

    tax.get_rank_lineage("g__Escherichia")
    # ['root', 'domain', 'phylum', 'class', 'order', 'family', 'genus']

    tax.get_lineage("g__Escherichia", ranks=["class", "family", "genus"])
    # ['c__Gammaproteobacteria', 'f__Enterobacteriaceae', 'g__Escherichia']

    tax.get_lineage("g__Escherichia", root_node="p__Proteobacteria")
    # ['p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']

    tax.stats()
    # {'nodes': 45503, 'ranks': 45503, 'names': 45503, 'unique_ranks': 8, ('nodes', 'class'): 379, ('nodes', 'domain'): 2, ('nodes', 'species'): 31910, ('nodes', 'order'): 1034, ('nodes', 'genus'): 9428, ('nodes', 'root'): 1, ('nodes', 'phylum'): 149, ('nodes', 'family'): 2600}

    #
    # The same goes for the other taxonomies
    #

    # NCBI
    from multitax.ncbitx import NcbiTx
    tax = NcbiTx(files="taxdump.tar.gz")
    tax.get_lineage("561")    
    # ['1', '131567', '2', '1224', '1236', '91347', '543', '561']

    # Silva
    from multitax.silvatx import SilvaTx
    tax = SilvaTx(files="tax_slv_ssu_138.1.txt.gz")
    tax.get_lineage("46463")    
    # ['1', '3', '2375', '3303', '46449', '46454', '46463']

    # Open Tree taxonomy
    from multitax.otttx import OttTx
    tax = OttTx(files="ott3.2.tgz")
    tax.get_lineage("474503")
    # ['805080', '93302', '844192', '248067', '822744', '768012', '424023', '474503']

    # GreenGenes
    from multitax.greengenestx import GreengenesTx
    tax = GreengenesTx(files="gg_13_5_taxonomy.txt.gz")
    tax.get_lineage("f__Enterobacteriaceae")
    # ['1', 'k__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacteriales', 'f__Enterobacteriaceae']

## General info

 - Taxonomies are parsed into nodes and annotated with names and ranks.
 - A single root node should be defined (root_node, root_parent, root_name, root_rank) and it is created when not provided.
 - Standard values for unknown/undefined nodes can be configured (unknown_node,unknown_name, unknown_rank)
 - Files parsed form disk or downloaded. When downloaded, they are handled in memory. It is possible to dump the file to disk with `output_prefix` parameter.

## LCA integration

Using pylca: https://github.com/pirovc/pylca

    from pylca.pylca import LCA
    from multitax.gtdbtx import GtdbTx

    tax = GtdbTx()
    L = LCA(tax._MultiTax__nodes)

    L("s__Escherichia dysenteriae", "s__Pseudomonas aeruginosa")
    # 'c__Gammaproteobacteria'
    
## Translation between taxonomies

Not yet implemented. The goal here is to map different taxonomies if the linkage data is available. That's what I think it will be possible.

 |        |NCBI   |GTDB   |SILVA   |OTT   |GG  |
 |--------|-------|-------|--------|------|----|
 |NCBI    |-      |part   |part    |part  |no  |
 |GTDB    |full   |-      |no      |no    |no  |
 |SILVA   |full   |no     |-       |part  |no  |
 |OTT     |part   |no     |part    |-     |no  |
 |GG      |no     |no     |no      |no    |-   |


## TODO list

- tests
- CustomTx
- improve stats
- check consistency
- filter
- write (tsv)
- translate

## Similar projects I know/found

- https://github.com/FOI-Bioinformatics/flextaxd
- https://github.com/shenwei356/taxonkit
- https://github.com/chanzuckerberg/taxoniq

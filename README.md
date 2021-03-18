# MultiTax

Pyhton library that provides a common interface to obtain, parse and interact with biological taxonomies (GTDB, NCBI, Silva, Greengenes, Open Tree taxonomy) + "Custom" and "Empty" taxonomies. 

## Goals
 
 - Fast, intuitive, generalied and easy to use library
 - Enable analysis from different tools outputs using different taxonomies
 - Enable tools to easily extend compatibility with multiple taxonomies without extra implementation effort

## Usage

    # GTDB
    from multitax.gtdbtx import GtdbTx
    tax = GtdbTx(files=["bac120_taxonomy.tsv.gz", "ar122_taxonomy.tsv.gz"])
    tax.get_lineage("g__Escherichia")
    tax.get_name_lineage("g__Escherichia")
    tax.get_rank_lineage("g__Escherichia")

    # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Enterobacteriaceae', 'g__Escherichia']
    # ['root', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia']
    # ['root', 'domain', 'phylum', 'class', 'order', 'family', 'genus']
    

    # NCBI
    from multitax.ncbitx import NcbiTx
    tax = NcbiTx(files="taxdump.tar.gz")
    tax.get_lineage("561")
    tax.get_name_lineage("561")
    tax.get_rank_lineage("561")
    
    # ['1', '131567', '2', '1224', '1236', '91347', '543', '561']
    # ['root', 'cellular organisms', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia']
    # ['root', 'no rank', 'superkingdom', 'phylum', 'class', 'order', 'family', 'genus']    

    # Silva
    from multitax.silvatx import SilvaTx
    tax = SilvaTx(files="tax_slv_ssu_138.1.txt.gz")
    tax.get_lineage("46463")
    tax.get_name_lineage("46463")
    tax.get_rank_lineage("46463")
    
    # ['1', '3', '2375', '3303', '46449', '46454', '46463']
    # ['root', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacterales', 'Enterobacteriaceae', 'Escherichia-Shigella']
    # ['root', 'domain', 'phylum', 'class', 'order', 'family', 'genus']

    # Open Tree taxonomy
    from multitax.otttx import OttTx
    tax = OttTx(files="ott3.2.tgz")
    tax.get_lineage("474503")
    tax.get_name_lineage("474503")
    tax.get_rank_lineage("474503")
    
    # ['805080', '93302', '844192', '248067', '822744', '768012', '424023', '474503']
    # ['root', 'cellular organisms', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacteriales', 'Enterobacteriaceae', 'Escherichia']
    # ['root', 'no rank', 'domain', 'phylum', 'class', 'order', 'family', 'genus']

    # GreenGenes
    from multitax.greengenestx import GreengenesTx
    tax = GreengenesTx(files="gg_13_5_taxonomy.txt.gz")
    tax.get_lineage("f__Enterobacteriaceae")
    tax.get_name_lineage("f__Enterobacteriaceae")
    tax.get_rank_lineage("f__Enterobacteriaceae")
    
    # ['1', 'k__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacteriales', 'f__Enterobacteriaceae']
    # ['root', 'Bacteria', 'Proteobacteria', 'Gammaproteobacteria', 'Enterobacteriales', 'Enterobacteriaceae']
    # ['root', 'kingdom', 'phylum', 'class', 'order', 'family']

## General info

 - Taxonomies are parsed into nodes and annotated with names and ranks.
 - A single root node should be defined (root_node, root_parent, root_name, root_rank) and it is created when not provided.
 - Standard values for unknown/undefined nodes can be configured (unknown_node,unknown_name, unknown_rank)

## Main functions

    get_parent(node) 
    get_parent_rank(node, rank)
    get_rank(node)
    get_name(node)
    get_node(name)
    get_latest(node) # ncbi and ott have history of changed taxids

    get_lineage(node, [root_node], [ranks])
    get_name_lineage(node, [root_node], [ranks])
    get_rank_lineage(node, [root_node], [ranks])

    stats()

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
|NCBI    |-      |parc   |parc    |parc  |no  |
|GTDB    |full   |-      |no      |no    |no  |
|SILVA   |full   |no     |-       |parc  |no  |
|OTT     |full   |no     |full    |-     |no  |
|GG      |no     |no     |no      |no    |-   |


## TODO list

- translate taxonomies
- check tree consistency
- filter tree
- pre-build lineages
- get sub-tree

## Similar projects I know/found

https://github.com/FOI-Bioinformatics/flextaxd
https://github.com/shenwei356/taxonkit
https://github.com/chanzuckerberg/taxoniq
#!/usr/bin/env python3


def main():

    print("GTDB")
    from multitax.gtdbtx import GtdbTx
    #tax = GtdbTx()
    tax = GtdbTx(files="files/bac120_taxonomy.tsv.gz")
    #tax = GtdbTx(files="files/bac120_taxonomy.tsv")
    #tax = GtdbTx(files=["files/bac120_taxonomy.tsv.gz", "files/ar122_taxonomy.tsv.gz"])
    print(tax.get_lineage("g__Escherichia"))
    print(tax.get_name_lineage("g__Escherichia"))
    print(tax.get_rank_lineage("g__Escherichia"))
    print()

    print("NCBI")
    from multitax.ncbitx import NcbiTx
    # tax = NcbiTx()
    tax = NcbiTx(files="files/taxdump.tar.gz")
    # tax = NcbiTx(files="files/nodes.dmp")
    # tax = NcbiTx(files=["files/nodes.dmp", "files/names.dmp"])
    # tax = NcbiTx(files=["files/nodes.dmp", "files/names.dmp", "files/merged.dmp"])
    print(tax.get_lineage("561"))
    print(tax.get_name_lineage("561"))
    print(tax.get_rank_lineage("561"))
    print()

    print("Silva")
    from multitax.silvatx import SilvaTx
    # tax = SilvaTx()
    tax = SilvaTx(files="files/tax_slv_ssu_138.1.txt.gz")
    # tax = SilvaTx(files="files/tax_slv_ssu_138.1.txt")
    print(tax.get_lineage("46463"))
    print(tax.get_name_lineage("46463"))
    print(tax.get_rank_lineage("46463"))
    print()

    print("Open Tree taxonomy")
    from multitax.otttx import OttTx
    # tax = OttTx()
    tax = OttTx(files="files/ott3.2.tgz")
    # tax = OttTx(files="files/taxonomy.tsv")
    # tax = OttTx(files=["files/taxonomy.tsv", "files/forwards.tsv"])
    print(tax.get_lineage("474503"))
    print(tax.get_name_lineage("474503"))
    print(tax.get_rank_lineage("474503"))
    print()

    print("GreenGenes")
    from multitax.greengenestx import GreengenesTx
    # tax = GreengenesTx()
    tax = GreengenesTx(files="files/gg_13_5_taxonomy.txt.gz")
    # tax = GreengenesTx(files="files/gg_13_5_taxonomy.txt")
    print(tax.get_lineage("f__Enterobacteriaceae"))
    print(tax.get_name_lineage("f__Enterobacteriaceae"))
    print(tax.get_rank_lineage("f__Enterobacteriaceae"))
    print()

if __name__ == "__main__":
    main()

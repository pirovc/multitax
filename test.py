#!/usr/bin/env python3


def main():

    print("GTDB")
    from multitax.gtdbtx import GtdbTx
    tax = GtdbTx(files=["bac120_taxonomy.tsv.gz", "ar122_taxonomy.tsv.gz"])
    print(tax.get_lineage("g__Escherichia"))
    print(tax.get_name_lineage("g__Escherichia"))
    print(tax.get_rank_lineage("g__Escherichia"))
    print()

    print("NCBI")
    from multitax.ncbitx import NcbiTx
    tax = NcbiTx(files="taxdump.tar.gz")
    print(tax.get_lineage("561"))
    print(tax.get_name_lineage("561"))
    print(tax.get_rank_lineage("561"))
    print()

    print("Silva")
    from multitax.silvatx import SilvaTx
    tax = SilvaTx(files="tax_slv_ssu_138.1.txt.gz")
    print(tax.get_lineage("46463"))
    print(tax.get_name_lineage("46463"))
    print(tax.get_rank_lineage("46463"))
    print()

    print("Open Tree taxonomy")
    from multitax.otttx import OttTx
    tax = OttTx(files="ott3.2.tgz")
    print(tax.get_lineage("474503"))
    print(tax.get_name_lineage("474503"))
    print(tax.get_rank_lineage("474503"))
    print()

    print("GreenGenes")
    from multitax.greengenestx import GreengenesTx
    tax = GreengenesTx(files="gg_13_5_taxonomy.txt.gz")
    print(tax.get_lineage("f__Enterobacteriaceae"))
    print(tax.get_name_lineage("f__Enterobacteriaceae"))
    print(tax.get_rank_lineage("f__Enterobacteriaceae"))
    print()

if __name__ == "__main__":
    main()

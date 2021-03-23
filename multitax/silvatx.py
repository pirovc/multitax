from .multitax import MultiTax


class SilvaTx(MultiTax):

    _urls = ["https://www.arb-silva.de/fileadmin/silva_databases/current/Exports/taxonomy/tax_slv_ssu_138.1.txt.gz"]
    _root_node = "1"

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'SilvaTx({})'.format(', '.join(args))

    def parse(self, fhs):
        nodes = {}
        ranks = {}
        names = {}

        lin = {}
        for source, fh in fhs.items():
            for line in fh:
                try:
                    name_lineage, taxid, rank, _ = line.split('\t', 3)
                except:
                    name_lineage, taxid, rank, _ = line.decode().split('\t', 3)
                # Remove last char ";"
                lineage = name_lineage[:-1]
                name = lineage.split(";")[-1]
                # Save lineage to build tree
                lin[lineage] = taxid
                names[taxid] = name
                ranks[taxid] = rank

        # Build parent node connection
        for lineage, taxid in lin.items():
            t = taxid
            l = lineage.split(";")[:-1]
            while l:
                parent_taxid = lin[";".join(l)]
                if t not in nodes:
                    nodes[t] = parent_taxid
                t = parent_taxid
                del l[-1] # remove last element
            # Connect last node to root
            if t not in nodes:
                nodes[t] = self.root_node

        return nodes, ranks, names

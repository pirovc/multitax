from multitax.multitax import MultiTax
from multitax.utils import open_files, download_files, write_close_files


class SilvaTx(MultiTax):

    __urls = ["https://www.arb-silva.de/fileadmin/silva_databases/current/Exports/taxonomy/tax_slv_ssu_138.1.txt.gz"]

    def __init__(self, files: list=[], **kwargs):
        # Set root node to use while parsing
        if "root_node" in kwargs and kwargs["root_node"] is not None:
            self.root_node = kwargs["root_node"]

        fhs = open_files(files) if files else download_files(self.__urls, **kwargs)
        self._MultiTax__nodes, self._MultiTax__ranks, self._MultiTax__names = self.parse(fhs.values())
        write_close_files(fhs, **kwargs)

        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'SilvaTx({})'.format(', '.join(args))

    def parse(self, fhs):
        nodes = {}
        ranks = {}
        names = {}

        lin = {}
        for fh in fhs:
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

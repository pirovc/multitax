from multitax.multitax import MultiTax
from multitax.utils import open_files, download_files, write_close_files


class GtdbTx(MultiTax):

    __urls = ["https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/ar122_taxonomy.tsv.gz",
              "https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/bac120_taxonomy.tsv.gz"]

    __rank_codes = [("d__", "domain"),
                    ("p__", "phylum"),
                    ("c__", "class"),
                    ("o__", "order"),
                    ("f__", "family"),
                    ("g__", "genus"),
                    ("s__", "species")]

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
        return 'GtdbTx({})'.format(', '.join(args))

    def parse(self, fhs):
        nodes = {}
        ranks = {}
        names = {}
        for fh in fhs:
            for line in fh:
                try:
                    _, lineage = line.rstrip().split('\t')
                except:
                    _, lineage = line.decode().rstrip().split('\t')
                lin = lineage.split(";")
                for i in range(len(lin))[::-1]:
                    # assert rank
                    assert lin[i][:3]==self.__rank_codes[i][0]
                    # taxid = "c__Deinococci", rank = "class", name = "Deinococci"
                    taxid = lin[i]
                    name = lin[i][3:]
                    if not name: continue # empty entry "s__"
                    rank = self.__rank_codes[i][1]
                    if i==0:
                        parent_taxid = self.root_node
                    else:
                        parent_taxid = lin[i-1]
                    if taxid not in nodes:
                        nodes[taxid] = parent_taxid
                        names[taxid] = name
                        ranks[taxid] = rank

        return nodes, ranks, names

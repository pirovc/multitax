from .multitax import MultiTax


class GtdbTx(MultiTax):

    _default_urls = ["https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/ar122_taxonomy.tsv.gz",
                     "https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/bac120_taxonomy.tsv.gz"]
    _rank_codes = [("d__", "domain"),
                   ("p__", "phylum"),
                   ("c__", "class"),
                   ("o__", "order"),
                   ("f__", "family"),
                   ("g__", "genus"),
                   ("s__", "species")]

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'GtdbTx({})'.format(', '.join(args))

    def _parse(self, fhs):
        nodes = {}
        ranks = {}
        names = {}
        for source, fh in fhs.items():
            for line in fh:
                try:
                    _, lineage = line.rstrip().split('\t')
                except:
                    _, lineage = line.decode().rstrip().split('\t')
                lin = lineage.split(";")
                for i in range(len(lin))[::-1]:
                    # assert rank
                    assert lin[i][:3] == self._rank_codes[i][0]
                    # taxid = "c__Deinococci", rank = "class", name = "Deinococci"
                    taxid = lin[i]
                    name = lin[i][3:]
                    # empty entry "s__"
                    if not name:
                        continue
                    rank = self._rank_codes[i][1]
                    if i == 0:
                        parent_taxid = self._default_root_node
                    else:
                        parent_taxid = lin[i-1]
                    if taxid not in nodes:
                        nodes[taxid] = parent_taxid
                        names[taxid] = name
                        ranks[taxid] = rank

        return nodes, ranks, names

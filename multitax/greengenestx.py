from .multitax import MultiTax
import warnings


class GreengenesTx(MultiTax):
    _default_urls = [
        "https://gg-sg-web.s3-us-west-2.amazonaws.com/downloads/greengenes_database/gg_13_5/gg_13_5_taxonomy.txt.gz"]
    _rank_codes = [("k__", "kingdom"),
                   ("p__", "phylum"),
                   ("c__", "class"),
                   ("o__", "order"),
                   ("f__", "family"),
                   ("g__", "genus"),
                   ("s__", "species")]

    def __init__(self, **kwargs):
        # forwards.tsv
        self._forwards = {}
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'GreengenesTx({})'.format(', '.join(args))

    def _build_translation(self, target_tax, files: list = None, urls: list = None):
        warnings.warn("Translation between taxonomies [" + self.__class__.__name__ +
                      "," + target_tax.__class__.__name__ + "] not yet implemented.")
        return {}

    def _parse(self, fhs, **kwargs):
        nodes = {}
        ranks = {}
        names = {}

        for source, fh in fhs.items():
            for line in fh:
                try:
                    _, lineage = line.rstrip().split('\t')
                except:
                    _, lineage = line.decode().rstrip().split('\t')
                lin = lineage.split("; ")
                for i in range(len(lin))[::-1]:
                    # assert rank
                    assert lin[i][:3] == self._rank_codes[i][0]
                    # taxid = "c__Deinococci", rank = "class", name = "Deinococci"
                    taxid = lin[i]
                    name = lin[i][3:]
                    if not name:
                        continue  # empty entry "s__"
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

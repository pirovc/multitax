from .multitax import MultiTax
import warnings


class GreengenesTx(MultiTax):
    _default_urls = [
        "https://ftp.microbio.me/greengenes_release/current/2024.09.taxonomy.id.tsv.gz"
    ]
    _rank_codes = [
        ("d__", "domain"),
        ("p__", "phylum"),
        ("c__", "class"),
        ("o__", "order"),
        ("f__", "family"),
        ("g__", "genus"),
        ("s__", "species"),
    ]

    def __init__(self, **kwargs):
        # forwards.tsv
        self._forwards = {}
        super().__init__(**kwargs)

    def __repr__(self):
        stats = ["{}={}".format(k, repr(v)) for (k, v) in self.stats().items()]
        return "GreengenesTx({})".format(", ".join(stats))

    def _build_translation(self, target_tax, files: list = None, urls: list = None):
        warnings.warn(
            "Translation between taxonomies ["
            + self.__class__.__name__
            + ","
            + target_tax.__class__.__name__
            + "] not yet implemented."
        )
        return {}

    def _parse(self, fhs, **kwargs):
        nodes = {}
        ranks = {}
        names = {}

        lineages = set()
        for source, fh in fhs.items():
            for line in fh:
                try:
                    fields = line.rstrip().split("\t")
                except TypeError:
                    fields = line.decode().rstrip().split("\t")

                # skip header
                if fields[0] == "Feature ID":
                    continue

                lineages.add(fields[1])

        for lineage in lineages:
            last_taxid = None
            lin = lineage.split("; ")
            for i in range(len(lin))[::-1]:
                # assert rank
                assert lin[i][:3] == self._rank_codes[i][0]

                name = lin[i][3:]
                if not name:
                    continue  # empty entry "s__"

                # taxid = "c__Deinococci", rank = "class", name = "Deinococci"
                taxid = lin[i]
                rank = self._rank_codes[i][1]

                if taxid not in nodes:
                    names[taxid] = name
                    ranks[taxid] = rank
                if last_taxid:
                    nodes[last_taxid] = taxid
                last_taxid = taxid
            nodes[last_taxid] = self._default_root_node

        return nodes, ranks, names

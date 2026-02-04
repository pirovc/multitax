from .multitax import MultiTax
import warnings


class SilvaTx(MultiTax):
    _default_urls = [
        "https://www.arb-silva.de/fileadmin/silva_databases/current/Exports/taxonomy/tax_slv_ssu_138.1.txt.gz"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        stats = ["{}={}".format(k, repr(v)) for (k, v) in self.stats().items()]
        return "SilvaTx({})".format(", ".join(stats))

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

        lin = {}
        for source, fh in fhs.items():
            for line in fh:
                try:
                    name_lineage, taxid, rank, _ = line.split("\t", 3)
                except TypeError:
                    name_lineage, taxid, rank, _ = line.decode().split("\t", 3)
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
            lsplit = lineage.split(";")[:-1]
            while lsplit:
                parent_taxid = lin[";".join(lsplit)]
                if t not in nodes:
                    nodes[t] = parent_taxid
                t = parent_taxid
                del lsplit[-1]  # remove last element
            # Connect last node to root
            if t not in nodes:
                nodes[t] = self._default_root_node

        return nodes, ranks, names

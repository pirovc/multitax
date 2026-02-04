from .multitax import MultiTax
from multitax.utils import open_files
from multitax.utils import download_files
import warnings


class GtdbTx(MultiTax):
    _default_urls = [
        "https://data.gtdb.aau.ecogenomic.org/releases/latest/ar53_taxonomy.tsv.gz",
        "https://data.gtdb.aau.ecogenomic.org/releases/latest/bac120_taxonomy.tsv.gz",
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
        super().__init__(**kwargs)

    def __repr__(self):
        stats = ["{}={}".format(k, repr(v)) for (k, v) in self.stats().items()]
        return "GtdbTx({})".format(", ".join(stats))

    def _build_translation(self, target_tax, files: list = None, urls: list = None):
        translated_nodes = {}
        if target_tax.__class__.__name__ == "NcbiTx":
            if files:
                fhs = open_files(files)
            else:
                _urls = [
                    "https://data.gtdb.aau.ecogenomic.org/releases/latest/ar53_metadata.tsv.gz",
                    "https://data.gtdb.aau.ecogenomic.org/releases/latest/bac120_metadata.tsv.gz",
                ]
                fhs = download_files(urls=urls if urls else _urls, retry_attempts=3)

            accession_col = 0
            gtdb_taxonomy_col = 19
            ncbi_taxid_col = 80

            for source, fh in fhs.items():
                for line in fh:
                    try:
                        fields = line.rstrip().split("\t")
                    except TypeError:
                        fields = line.decode().rstrip().split("\t")

                    # skip header
                    if fields[accession_col] == "accession":
                        continue

                    ncbi_leaf_node = target_tax.latest(fields[ncbi_taxid_col])
                    if ncbi_leaf_node != target_tax.undefined_node:
                        ncbi_nodes = target_tax.lineage(
                            ncbi_leaf_node,
                            ranks=[
                                "domain",
                                "phylum",
                                "class",
                                "order",
                                "family",
                                "genus",
                                "species",
                            ],
                        )
                    else:
                        continue

                    # Build GTDB lineage from leaf (species on given lineage)
                    # to accomodate possible changes in the loaded tax
                    gtdb_leaf_node = fields[gtdb_taxonomy_col].split(";")[-1]
                    if gtdb_leaf_node != self.undefined_node:
                        gtdb_nodes = self.lineage(
                            gtdb_leaf_node,
                            ranks=[
                                "domain",
                                "phylum",
                                "class",
                                "order",
                                "family",
                                "genus",
                                "species",
                            ],
                        )
                    else:
                        continue

                    # Match ranks
                    for i, gtdb_n in enumerate(gtdb_nodes):
                        if (
                            ncbi_nodes[i] != target_tax.undefined_node
                            and gtdb_n != self.undefined_node
                        ):
                            if gtdb_n not in translated_nodes:
                                translated_nodes[gtdb_n] = set()
                            translated_nodes[gtdb_n].add(ncbi_nodes[i])

        else:
            warnings.warn(
                "Translation between taxonomies ["
                + self.__class__.__name__
                + ","
                + target_tax.__class__.__name__
                + "] not yet implemented."
            )

        return translated_nodes

    def _parse(self, fhs, **kwargs):
        nodes = {}
        ranks = {}
        names = {}
        for source, fh in fhs.items():
            for line in fh:
                try:
                    _, lineage = line.rstrip().split("\t")
                except TypeError:
                    _, lineage = line.decode().rstrip().split("\t")
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
                        parent_taxid = lin[i - 1]
                    if taxid not in nodes:
                        nodes[taxid] = parent_taxid
                        names[taxid] = name
                        ranks[taxid] = rank

        return nodes, ranks, names

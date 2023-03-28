from .multitax import MultiTax
from .utils import check_file
from .utils import open_files
from .utils import download_files
import warnings


class GtdbTx(MultiTax):

    _default_urls = ["https://data.gtdb.ecogenomic.org/releases/latest/ar53_taxonomy.tsv.gz",
                     "https://data.gtdb.ecogenomic.org/releases/latest/bac120_taxonomy.tsv.gz"]
    _rank_codes = [("d__", "domain"),
                   ("p__", "phylum"),
                   ("c__", "class"),
                   ("o__", "order"),
                   ("f__", "family"),
                   ("g__", "genus"),
                   ("s__", "species")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'GtdbTx({})'.format(', '.join(args))

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

    def _translate(self, target_tax, files: list = None, urls: list = None):
        translated_nodes = {}
        if target_tax.__class__.__name__ == "NcbiTx":

            if files:
                fhs = open_files(files)
            else:
                _default_urls = ["https://data.gtdb.ecogenomic.org/releases/latest/ar53_metadata.tar.gz",
                                 "https://data.gtdb.ecogenomic.org/releases/latest/bac120_metadata.tar.gz"]
                fhs = download_files(
                    urls=urls if urls else _default_urls, retry_attempts=3)

            for source, fh in fhs.items():
                for file in fh.getmembers():
                    with fh.extractfile(file) as ext:
                        for line in ext:
                            try:
                                fields = line.rstrip().split('\t')
                            except:
                                fields = line.decode().rstrip().split('\t')

                            # skip header
                            if fields[0] == "accession":
                                continue

                            gtdb_nodes = fields[16].split(";")
                            ncbi_leaf_node = target_tax.latest(fields[77])
                            if ncbi_leaf_node != target_tax.undefined_node:
                                ncbi_nodes = target_tax.lineage(ncbi_leaf_node, ranks=[
                                                                "superkingdom",
                                                                "phylum",
                                                                "class",
                                                                "order",
                                                                "family",
                                                                "genus",
                                                                "species"])
                            else:
                                continue

                            for i, gtdb_n in enumerate(gtdb_nodes):
                                if ncbi_nodes[i] != target_tax.undefined_node:
                                    if self.latest(gtdb_n) != self.undefined_node:
                                        if gtdb_n not in translated_nodes:
                                            translated_nodes[gtdb_n] = set()
                                        translated_nodes[gtdb_n].add(
                                            ncbi_nodes[i])

                            # 0 accession
                            # 16 gtdb_taxonomy
                            # 77 ncbi_taxid
                            # 78 ncbi_taxonomy
                            # 79 ncbi_taxonomy_unfiltered
                            # print(fields)

        else:
            warnings.warn("translation between taxonomies not yet implemented")

        return translated_nodes

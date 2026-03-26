from .multitax import MultiTax
from multitax.utils import close_files, open_files, download_files, format_repr
import warnings


class GtdbTx(MultiTax):
    _default_version = "226"
    _supported_versions = [
        "80",
        "83",
        "86.2",
        "89",
        "95",
        "202",
        "207",
        "214.1",
        "220",
        "226",
    ]

    _url_prefix = "https://data.gtdb.ecogenomic.org/releases/"
    _default_urls = {
        "80": [f"{_url_prefix}release80/80.0/bac_taxonomy_r80.tsv"],
        "83": [f"{_url_prefix}release83/83.0/bac_taxonomy_r83.tsv"],
        "86.2": [
            f"{_url_prefix}release86/86.2/ar122_taxonomy_r86.2.tsv",
            f"{_url_prefix}release86/86.2/bac120_taxonomy_r86.2.tsv",
        ],
        "89": [
            f"{_url_prefix}release89/89.0/ar122_taxonomy_r89.tsv",
            f"{_url_prefix}release89/89.0/bac120_taxonomy_r89.tsv",
        ],
        "95": [
            f"{_url_prefix}release95/95.0/ar122_taxonomy_r95.tsv.gz",
            f"{_url_prefix}release95/95.0/bac120_taxonomy_r95.tsv.gz",
        ],
        "202": [
            f"{_url_prefix}release202/202.0/ar122_taxonomy_r202.tsv.gz",
            f"{_url_prefix}release202/202.0/bac120_taxonomy_r202.tsv.gz",
        ],
        "207": [
            f"{_url_prefix}release207/207.0/ar53_taxonomy_r207.tsv.gz",
            f"{_url_prefix}release207/207.0/bac120_taxonomy_r207.tsv.gz",
        ],
        "214.1": [
            f"{_url_prefix}release214/214.1/ar53_taxonomy_r214.tsv.gz",
            f"{_url_prefix}release214/214.1/bac120_taxonomy_r214.tsv.gz",
        ],
        "220": [
            f"{_url_prefix}release220/220.0/ar53_taxonomy_r220.tsv.gz",
            f"{_url_prefix}release220/220.0/bac120_taxonomy_r220.tsv.gz",
        ],
        "226": [
            f"{_url_prefix}release226/226.0/ar53_taxonomy_r226.tsv.gz",
            f"{_url_prefix}release226/226.0/bac120_taxonomy_r226.tsv.gz",
        ],
    }

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
        self._convert_to = {}
        self._convert_from = {}
        super().__init__(**kwargs)

    def __repr__(self):
        return format_repr(inst=self)

    def _build_translation(self, target_tax, file: str = None, url: str = None):
        translated_nodes = {}
        if target_tax.__class__.__name__ == "NcbiTx":
            if file:
                fhs = open_files([file])
            else:
                if not url:
                    url = f"https://github.com/pirovc/multitax/raw/refs/heads/main/data/gtdb/{self.version}_acc_rep_lin_ncbi.tsv.gz"
                fhs = download_files(urls=[url], retry_attempts=3)

            accession_col = 0
            gtdb_taxonomy_col = 2
            ncbi_taxid_col = 3

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

            close_files(fhs)
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

    def _lookup_version_taxa(self, node, version: str):
        res = set()
        for acc in self._convert_from.get(node, ""):
            for tx in self._convert_to[version].get(acc, "").split(";"):
                # Return only rank of requested node
                if tx.startswith(node[:1]):
                    res.add(tx)
        return res

    def _download_parse_version_taxa(self, version, file, url):
        if file:
            fhs = open_files(files=[file])
        else:
            if not url:
                # url = f"https://github.com/pirovc/multitax/raw/refs/heads/main/data/gtdb/{version}_acc_rep_tax.tsv.gz"
                url = f"file:///home/pirov/code/multitax/data/gtdb/{version}_acc_rep_lin_ncbi.tsv.gz"
            fhs = download_files(urls=[url], retry_attempts=3)

        for fh in fhs.values():
            for line in fh:
                try:
                    yield line.rstrip().split("\t")
                except TypeError:
                    yield line.decode().rstrip().split("\t")

    def build_conversion(
        self,
        version: str,
        files: [str, str] = ("", ""),
        urls: tuple[str, str] = ("", ""),
    ):
        """
        Download and build conversion table between two versions.
        Optional function, conversion tables are automatically downloaded
        and built on first .convert() call.
        """
        if version not in self._supported_versions:
            raise ValueError(
                f"Version [{version}] not supported for conversion: {', '.join(self._supported_versions)}"
            )

        if not self._convert_from:
            # Collect the accessions of the representative entries for each taxa in the current version
            for acc, rep, lin, _ in self._download_parse_version_taxa(
                version=self.version, file=files[0], url=urls[0]
            ):
                if rep == "t":
                    for tx in lin.split(";"):
                        if tx not in self._convert_from:
                            self._convert_from[tx] = []
                        self._convert_from[tx].append(acc)

        if version not in self._convert_to:
            # Collect the lineage for each accession
            acc_lin = {}
            for acc, _, lin, _ in self._download_parse_version_taxa(
                version=version, file=files[1], url=urls[1]
            ):
                acc_lin[acc] = lin
            # Assign only at the end, in case of download or parse errors
            self._convert_to[version] = acc_lin

    def convert(self, node: str, version: str) -> set[str]:
        """
        Converts a taxonomic node from current version to another.
        It uses a genomic centric strategy, based on the taxa of the representative
        genome among versions.
        It may return multiple nodes for ranks above species,
        since multiple representatives can be split into more taxa.
        It may return an empty set if node is not found in the current version
        or if related representative is no longer available in the requested version.

        Example:

            from multitax import GtdbTx
            tax = GtdbTx(version="95")

            # Species - always one-to-one
            tax.convert('s__Giesbergeria metamorpha', version="226")
            {'s__Simplicispira metamorpha'}

            # Other ranks - may be one-to-many
            tax.convert('g__UBA6715', version="226")
            {'g__Aquirufa', 'g__Sandaracinomonas'}
        """

        if version not in self._supported_versions:
            raise ValueError(
                f"Version [{version}] not supported: {', '.join(self._supported_versions)}"
            )

        if not self._convert_from or version not in self._convert_to:
            self.build_conversion(version=version)

        return self._lookup_version_taxa(node, version)

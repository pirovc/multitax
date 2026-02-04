from .multitax import MultiTax
from multitax.utils import filter_function
import warnings


class OttTx(MultiTax):
    _default_urls = ["https://files.opentreeoflife.org/ott/ott3.7.3/ott3.7.3.tgz"]
    _default_root_node = "805080"

    def __init__(self, **kwargs):
        self._forwards = {}
        self._extended_name_nodes = {}
        super().__init__(**kwargs)

    def __repr__(self):
        stats = ["{}={}".format(k, repr(v)) for (k, v) in self.stats().items()]
        return "OttTx({})".format(", ".join(stats))

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
        fhs_list = list(fhs.values())
        if len(fhs_list) == 1 and list(fhs)[0].endswith(".tgz"):
            nodes, ranks, names = self._parse_ott(
                fhs_list[0], extended_names=kwargs["extended_names"]
            )
        else:
            # nodes.dmp
            nodes, ranks, names = self._parse_taxonomy(fhs_list[0])
            # [forwards.tsv]
            if len(fhs) >= 2:
                self._forwards = self._parse_forwards(fhs_list[1])
            if len(fhs) == 3 and kwargs["extended_names"]:
                self._extended_name_nodes = self._parse_synonyms(fhs_list[2])

        return nodes, ranks, names

    def _parse_forwards(self, fh):
        forwards = {}
        # skip first line header
        next(fh)
        for line in fh:
            try:
                old_taxid, new_taxid = line.rstrip().split("\t")
            except TypeError:
                old_taxid, new_taxid = line.decode().rstrip().split("\t")
            forwards[old_taxid] = new_taxid
        return forwards

    def _parse_ott(self, fh_taxdump, extended_names):
        # Get files inside folder by name
        for e in fh_taxdump.getnames():
            if e.endswith("taxonomy.tsv"):
                tax = e
            if e.endswith("forwards.tsv"):
                fwr = e
            if e.endswith("synonyms.tsv"):
                syn = e

        with fh_taxdump.extractfile(tax) as fh_nodes:
            nodes, ranks, names = self._parse_taxonomy(fh_nodes)
        with fh_taxdump.extractfile(fwr) as fh_forwards:
            self._forwards = self._parse_forwards(fh_forwards)
        if extended_names:
            with fh_taxdump.extractfile(syn) as fh_synonyms:
                self._extended_name_nodes = self._parse_synonyms(fh_synonyms)
        return nodes, ranks, names

    def _parse_synonyms(self, fh):
        synonyms = {}
        # skip first line header
        next(fh)
        for line in fh:
            try:
                name, taxid, _ = line.split("\t|\t", 2)
            except TypeError:
                name, taxid, _ = line.decode().split("\t|\t", 2)
            if name not in synonyms:
                synonyms[name] = []
            synonyms[name].append(taxid)

        return synonyms

    def _parse_taxonomy(self, fh):
        nodes = {}
        ranks = {}
        names = {}
        # skip first line header
        next(fh)
        for line in fh:
            try:
                taxid, parent_taxid, name, rank, _ = line.split("\t|\t", 4)
            except TypeError:
                taxid, parent_taxid, name, rank, _ = line.decode().split("\t|\t", 4)
            ranks[taxid] = rank
            nodes[taxid] = parent_taxid
            names[taxid] = name
        return nodes, ranks, names

    def forwards(self, node: str):
        """
        Returns relative entry from the forwards.tsv file of a given node.
        """
        if node in self._forwards:
            return self._forwards[node]
        else:
            return self.undefined_node

    def latest(self, node: str):
        n = super().latest(node)
        if n == self.undefined_node:
            n = self.forwards(node)
        return n

    def search_name(
        self,
        text: str,
        rank: str = None,
        exact: bool = True,
        force_extended: bool = False,
    ):
        """
        Search node by exact or partial name.

        Default order (can be skipped with **force_extended=True**):

        1) Search default names defined on "taxonomy.tsv"

        2) If nothing was found, search in all other names defined on "synonyms.tsv" (must be activated with OttTx(**extended_names=True**))

        Parameters:
        * **text** *[str]*: Text to search.
        * **rank** *[str]*: Filter results by rank.
        * **exact** *[bool]*: Exact or partial name search (both case sensitive).
        * **force_extended** *[bool]*: Search for text in all categories at once.

        Returns: list of matching nodes
        """
        n = super().search_name(text, rank=rank, exact=exact)
        if n and not force_extended:
            return n
        else:
            if exact:
                ret = self._exact_name(text, self._extended_name_nodes)
            else:
                ret = self._partial_name(text, self._extended_name_nodes)

            # Only return nodes of chosen rank
            if rank:
                ret = filter_function(ret, self.rank, rank)

            return list(set(n + ret))

    def stats(self):
        s = super().stats()
        if self._forwards:
            s["forwards"] = len(self._forwards)
        if self._extended_name_nodes:
            s["extended_names"] = len(self._extended_name_nodes)
        return s

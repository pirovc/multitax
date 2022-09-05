from .multitax import MultiTax
from .utils import filter_function


class NcbiTx(MultiTax):
    _default_urls = ["ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"]

    def __init__(self, **kwargs):
        self._merged = {}
        self._extended_name_nodes = {}
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'NcbiTx({})'.format(', '.join(args))

    def _parse(self, fhs, **kwargs):
        fhs_list = list(fhs.values())
        # One element tar.gz -> taxdump.tar.gz
        if len(fhs_list) == 1 and list(fhs)[0].endswith(".tar.gz"):
            nodes, ranks, names, self._merged = self._parse_taxdump(
                fhs_list[0], extended_names=kwargs["extended_names"])
        else:
            # nodes.dmp
            nodes, ranks = self._parse_nodes(fhs_list[0])

            # [names.dmp]
            if len(fhs) >= 2:
                names = self._parse_names(
                    fhs_list[1], extended_names=kwargs["extended_names"])
            else:
                names = {}

            # [merged.dmp]
            if len(fhs) == 3:
                self._merged = self._parse_merged(fhs_list[2])
        return nodes, ranks, names

    def _parse_taxdump(self, fh_taxdump, extended_names):
        with fh_taxdump.extractfile('nodes.dmp') as fh_nodes:
            nodes, ranks = self._parse_nodes(fh_nodes)
        with fh_taxdump.extractfile('names.dmp') as fh_names:
            names = self._parse_names(fh_names, extended_names=extended_names)
        with fh_taxdump.extractfile('merged.dmp') as fh_merged:
            merged = self._parse_merged(fh_merged)
        return nodes, ranks, names, merged

    def _parse_nodes(self, fh):
        nodes = {}
        ranks = {}
        for line in fh:
            try:
                taxid, parent_taxid, rank, _ = line.split('\t|\t', 3)
            except:
                taxid, parent_taxid, rank, _ = line.decode().split('\t|\t', 3)
            ranks[taxid] = rank
            nodes[taxid] = parent_taxid
        return nodes, ranks

    def _parse_names(self, fh, extended_names):
        names = {}
        for line in fh:
            try:
                node, name, _, name_class = line.split('\t|\t')
            except:
                node, name, _, name_class = line.decode().split('\t|\t')
            if name_class.replace('\t|\n', '') == "scientific name":
                names[node] = name
            elif extended_names:
                if name not in self._extended_name_nodes:
                    self._extended_name_nodes[name] = []
                self._extended_name_nodes[name].append(node)

        return names

    def _parse_merged(self, fh):
        merged = {}
        for line in fh:
            try:
                old_taxid, _, new_taxid, _ = line.split('\t', 3)
            except:
                old_taxid, _, new_taxid, _ = line.decode().split('\t', 3)
            merged[old_taxid] = new_taxid
        return merged

    def merged(self, node: str):
        """
        Returns relative entry from the merged.dmp file of a given node.
        """
        if node in self._merged:
            return self._merged[node]
        else:
            return self.undefined_node

    def latest(self, node: str):
        n = super().latest(node)
        if n == self.undefined_node:
            n = self.merged(node)
        return n

    def stats(self):
        s = super().stats()
        if self._merged:
            s["merged"] = len(self._merged)
        if self._extended_name_nodes:
            s["extended_names"] = len(self._extended_name_nodes)
        return s

    def search_name(self, text: str, rank: str = None, exact: bool = True, force_extended: bool = False):
        """
        Search node by exact or partial name.

        Default order (can be skipped with **force_extended=True**):

        1) Search names defined as "scientific name" on nodes.dmp

        2) If nothing was found, search text in all other categories (must be activated with NcbiTx(**extended_names=True**))

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

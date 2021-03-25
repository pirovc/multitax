from .multitax import MultiTax


class NcbiTx(MultiTax):
    _default_urls = ["ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"]

    def __init__(self, **kwargs):
        # [merged.dmp]
        self._merged = {}
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'NcbiTx({})'.format(', '.join(args))

    def _parse(self, fhs):
        fhs_list = list(fhs.values())
        # One element tar.gz -> taxdump.tar.gz
        if len(fhs_list) == 1 and list(fhs)[0].endswith(".tar.gz"):
            nodes, ranks, names, self._merged = self._parse_taxdump(fhs_list[0])
        else:
            # nodes.dmp
            nodes, ranks = self._parse_nodes(fhs_list[0])

            # [names.dmp]
            if len(fhs) >= 2:
                names = self._parse_names(fhs_list[1])
            else:
                names = {}

            # [merged.dmp]
            if len(fhs) == 3:
                self._merged = self._parse_merged(fhs_list[2])
        return nodes, ranks, names

    def _parse_taxdump(self, fh_taxdump):
        with fh_taxdump.extractfile('nodes.dmp') as fh_nodes:
            nodes, ranks = self._parse_nodes(fh_nodes)
        with fh_taxdump.extractfile('names.dmp') as fh_names:
            names = self._parse_names(fh_names)
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

    def _parse_names(self, fh):
        names = {}
        for line in fh:
            try:
                node, name, _, name_class = line.split('\t|\t')
            except:
                node, name, _, name_class = line.decode().split('\t|\t')
            if name_class.replace('\t|\n', '') == "scientific name":
                names[node] = name
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

    def merged(self, node):
        if node in self._merged:
            return self._merged[node]
        else:
            return self.unknown_node

    def latest(self, node):
        n = super().latest(node)
        if n == self.unknown_node:
            n = self.merged(node)
        return n

    def stats(self):
        s = super().stats()
        s["merged"] = len(self._merged)
        return s

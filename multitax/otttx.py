from multitax.multitax import MultiTax


class OttTx(MultiTax):

    default_urls = ["http://files.opentreeoflife.org/ott/ott3.2/ott3.2.tgz"]
    default_root_node = "805080"

    def __init__(self, **kwargs):
        # forwards.tsv
        self.__forwards = {}

        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'OttTx({})'.format(', '.join(args))

    def parse(self, fhs):
        fhs_list = list(fhs.values())
        if len(fhs_list) == 1 and list(fhs)[0].endswith(".tgz"):
            nodes, ranks, names, self.__forwards = self.parse_ott(fhs_list[0])
        else:
            # nodes.dmp
            nodes, ranks, names = self.parse_taxonomy(fhs_list[0])
            # [forwards.tsv]
            if len(fhs) == 2: self.__forwards = self.parse_forwards(fhs_list[1])
        return nodes, ranks, names

    def parse_ott(self, fh_taxdump):
        # Files inside folder
        for e in fh_taxdump.getnames():
            if e.endswith("taxonomy.tsv"):
                tax = e
            if e.endswith("forwards.tsv"):
                fwr = e
        with fh_taxdump.extractfile(tax) as fh_nodes:
            nodes, ranks, names = self.parse_taxonomy(fh_nodes)
        with fh_taxdump.extractfile(fwr) as fh_names:
            forwards = self.parse_forwards(fh_names)
        return nodes, ranks, names, forwards

    def parse_taxonomy(self, fh):
        nodes = {}
        ranks = {}
        names = {}
        for line in fh:
            try:
                taxid, parent_taxid, name, rank, _ = line.split('\t|\t', 4)
            except:
                taxid, parent_taxid, name, rank, _ = line.decode().split('\t|\t', 4)
            ranks[taxid] = rank
            nodes[taxid] = parent_taxid
            names[taxid] = name
        return nodes, ranks, names

    def parse_forwards(self, fh):
        forwards = {}
        for line in fh:
            try:
                old_taxid, new_taxid = line.rstrip().split('\t')
            except:
                old_taxid, new_taxid = line.decode().rstrip().split('\t')
            forwards[old_taxid] = new_taxid
        return forwards

    def get_forwards(self, node):
        if node in self.__forwards:
            return self.__forwards[node]
        else:
            return self.unknown_node

    def get_parent(self, node):
        n = super().get_parent(node)
        if n == self.unknown_node:
            n = super().get_parent(self.get_forwards(node))
        return n

    def get_latest(self, node):
        n = super().get_latest(node)
        if n == self.unknown_node:
            n = self.get_forwards(node)
        return n

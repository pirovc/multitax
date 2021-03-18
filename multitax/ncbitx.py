from multitax.multitax import MultiTax
from multitax.utils import open_files, download_files, write_close_files


class NcbiTx(MultiTax):

    # Default url
    __urls = ["ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz"]

    # merged.dmp
    __merged = {}

    # Default NCBI
    root_node = "1"

    def __init__(self, files: list=None, **kwargs):
        fhs = open_files(files) if files else download_files(self.__urls, **kwargs)
        self.__sources.extend(fhs.keys())
        fhs_list = list(fhs.values())
        # One element tar.gz -> taxdump.tar.gz
        if len(fhs_list) == 1 and list(fhs)[0].endswith(".tar.gz"):
            self._MultiTax__nodes, self._MultiTax__ranks, self._MultiTax__names, self.__merged = self.parse_taxdump(fhs_list[0])
        else:
            # nodes.dmp
            self._MultiTax__nodes, self._MultiTax__ranks = self.parse_nodes(fhs_list[0])
            # [names.dmp]
            if len(fhs) == 2: self._MultiTax__names = self.parse_names(fhs_list[1])
            # [merged.dmp]
            if len(fhs) == 3: self.__merged = self.parse_merged(fhs_list[2])
        
        write_close_files(fhs, **kwargs)
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'NcbiTx({})'.format(', '.join(args))

    def parse_taxdump(self, fh_taxdump):
        with fh_taxdump.extractfile('nodes.dmp') as fh_nodes:
            nodes, ranks = self.parse_nodes(fh_nodes)
        with fh_taxdump.extractfile('names.dmp') as fh_names:
            names = self.parse_names(fh_names)
        with fh_taxdump.extractfile('merged.dmp') as fh_merged:
            merged = self.parse_merged(fh_merged)
        return nodes, ranks, names, merged

    def parse_nodes(self, fh):
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

    def parse_names(self, fh):
        names = {}
        for line in fh:
            try:
                node, name, _, name_class = line.split('\t|\t')
            except:
                node, name, _, name_class = line.decode().split('\t|\t')
            if name_class.replace('\t|\n', '') == "scientific name":
                names[node] = name
        return names

    def parse_merged(self, fh):
        merged = {}
        for line in fh:
            try:
                old_taxid, _, new_taxid, _ = line.split('\t', 3)
            except:
                old_taxid, _, new_taxid, _ = line.decode().split('\t', 3)
            merged[old_taxid] = new_taxid
        return merged

    def get_merged(self, node):
        if node in self.__merged:
            return self.__merged[node]
        else:
            return self.unknown_node

    def get_parent(self, node):
        n = super().get_parent(node)
        if n == self.unknown_node:
            n = super().get_parent(self.get_merged(node))
        return n

    def get_latest(self, node):
        n = super().get_latest(node)
        if n == self.unknown_node:
            n = self.get_merged(node)
        return n

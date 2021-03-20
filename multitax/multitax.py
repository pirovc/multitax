from multitax.utils import open_files, download_files, close_files, check_file, check_dir


class MultiTax:

    __version = "0.1.0"

    unknown_node = None
    unknown_name = None
    unknown_rank = None

    root_node = "1"
    root_parent = "0"
    root_name = "root"
    root_rank = "root"

    __fixed_ranks = None
    __nodes = {}
    __names = {}
    __ranks = {}

    __name_nodes = {}
    __node_children = {}
    __lineages = {}

    __sources = []

    def __init__(self,
                 files: list=None,
                 urls: list=None,
                 output_prefix: str=None,
                 root_node: str=None,
                 root_parent: str=None,
                 root_name: str=None,
                 root_rank: str=None,
                 unknown_node: str=None,
                 unknown_name: str=None,
                 unknown_rank: str=None,
                 fixed_ranks: list=None,
                 build_lineages: bool=False,
                 build_node_names: bool=False,
                 build_node_children: bool=False):

        if files:
            if isinstance(files, str):
                files = [files]
            for file in files:
                check_file(file)

        if output_prefix:
            check_dir(output_prefix)

        if root_node is not None:
            self.root_node = root_node
        if root_parent is not None:
            self.root_parent = root_parent
        if root_name is not None:
            self.root_name = root_name
        if root_rank is not None:
            self.root_rank = root_rank
        if unknown_node is not None:
            self.unknown_node = unknown_node
        if unknown_name is not None:
            self.unknown_name = unknown_name
        if root_name is not None:
            self.unknown_rank = unknown_rank

        # open files from disk or download
        fhs = open_files(files) if files else download_files(default_urls=self.urls, custom_ulrs=urls, output_prefix=output_prefix)
        self.__nodes, self.__ranks, self.__names = self.parse(fhs)
        close_files(fhs)

        # Save sources for stats
        self.__sources.extend(fhs.keys())

        # Set root node in the tree
        self.__set_root_node()

        if fixed_ranks:
            self.__fixed_ranks = fixed_ranks
            # filter?

        if build_node_children:
            self.__set_node_children()

        if build_node_names:
            self.__set_node_names()

        if build_lineages:
            self.build_lineages()

    def __set_root_node(self):
        self.__nodes[self.root_node] = self.root_parent
        self.__ranks[self.root_node] = self.root_rank
        self.__names[self.root_node] = self.root_name

    def __set_node_names(self):
        # Reverse dict from names
        for k, v in self.__names.items():
            if v not in self.__name_nodes:
                self.__name_nodes[v] = []
            self.__name_nodes[v].append(k)

    def __set_node_children(self):
        # Reverse dict from nodes
        for k, v in self.__nodes.items():
            if v not in self.__node_children:
                self.__node_children[v] = []
            self.__node_children[v].append(k)

    def get_node(self, name):
        # Setup on first use
        if not self.__name_nodes:
            self.__set_node_names()
        if name in self.__name_nodes:
            return self.__name_nodes[name]
        else:
            return [self.unknown_node]

    def get_children(self, node):
        # Setup on first use
        if not self.__node_children:
            self.__set_node_children()
        if node in self.__node_children:
            return self.__node_children[node]
        else:
            return []

    def get_parent(self, node):
        if node in self.__nodes:
            return self.__nodes[node]
        else:
            return self.unknown_node

    def get_parent_rank(self, node, rank):
        while node not in [self.root_parent, self.unknown_node]:
            if self.get_rank(node) == rank:
                return node
            node = self.get_parent(node)
        return self.unknown_node

    def get_rank(self, node):
        if node in self.__ranks:
            return self.__ranks[node]
        else:
            return self.unknown_rank

    def get_name(self, node):
        if node in self.__names:
            return self.__names[node]
        else:
            return self.unknown_name

    def get_latest(self, node):
        if node in self.__nodes:
            return node
        else:
            return self.unknown_node

    def get_rank_lineage(self, node: str, root_node: str=None, ranks: list=None):
        return list(map(self.get_rank,
                        self.get_lineage(node=node,
                                         root_node=root_node,
                                         ranks=ranks)))

    def get_name_lineage(self, node: str, root_node: str=None, ranks: list=None):
        return list(map(self.get_name, 
                        self.get_lineage(node=node,
                                         root_node=root_node,
                                         ranks=ranks)))

    def get_lineage(self, node: str, root_node: str=None, ranks: list=None):
        # If pre-build and not special subset is required
        if node in self.__lineages and root_node is None and ranks is None:
            return self.__lineages[node]
        else:
            if root_node:
                root_parent = self.get_parent(root_node)
            else:
                root_parent = self.root_parent

            if not ranks:
                ranks = self.__fixed_ranks

            lin = []
            n = node
            if ranks:
                # Fixed length lineage
                lin = [self.unknown_node] * len(ranks)
                while n not in [root_parent, self.unknown_node]:
                    r = self.get_rank(n)
                    if r in ranks:
                        lin[ranks.index(r)] = n
                    n = self.get_parent(n)
                return lin
            else:
                # Full lineage
                while n not in [root_parent, self.unknown_node]:
                    lin.append(n)
                    n = self.get_parent(n)
                return lin[::-1]

    def stats(self):
        s = {}
        s["sources"] = self.__sources
        s["nodes"] = len(self.__nodes)
        s["ranks"] = len(self.__ranks)
        s["names"] = len(self.__ranks)
        unique_ranks = set(self.__ranks.values())
        s["unique_ranks"] = len(set(self.__ranks.values()))
        for ur in unique_ranks:
            s[("nodes", ur)] = list(self.__ranks.values()).count(ur)
        return s

    def build_lineages(self):
        for node in self.__nodes:
            self.__lineages[node] = self.get_lineage(node)

    # def get_sub_tree(node):
    #     pass
    # def get_leaf_nodes(self, node: str=None): # default, tax.root_node
    #     pass # get sub_tree?
    # def get_rank_nodes(self, rank: str):
    #     pass
    # def check_tree_consistency(self):
    #     pass
    # def filter(self, ranks: list=None, nodes: list=None, names: list=None):
    #     pass # filter itself


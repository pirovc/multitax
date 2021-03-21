from .utils import open_files, download_files, close_files, check_file, check_dir, reverse_dict


class MultiTax(object):

    version = "0.1.0"

    # Default values
    default_urls = []
    default_root_node = "1"

    def __init__(self,
                 files: list=None,
                 urls: list=None,
                 output_prefix: str=None,
                 root_node: str=None,
                 root_parent: str="0",
                 root_name: str="root",
                 root_rank: str="root",
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

        #filter?
        self.fixed_ranks = fixed_ranks
        #filter?
        self.root_node = root_node if root_node else self.default_root_node
        self.root_parent = root_parent
        self.root_name = root_name
        self.root_rank = root_rank
        self.unknown_node = unknown_node
        self.unknown_name = unknown_name
        self.unknown_rank = unknown_rank

        self.__lineages = {}
        self.__name_nodes = reverse_dict(self.__names) if build_node_names else {}
        self.__node_children = reverse_dict(self.__nodes) if build_node_children else {}

        # open files from disk or download
        if files:
            fhs = open_files(files)
        else:
            fhs = download_files(urls=urls if urls else self.default_urls,
                                 output_prefix=output_prefix)
        # Parse files
        self.__nodes, self.__ranks, self.__names = self.parse(fhs)
        close_files(fhs)

        # Save sources for stats (files or urls)
        self.sources = list(fhs.keys())

        # Set root node in the tree
        self.__set_root()

        if build_lineages:
            self.build_lineages()

    # main function to be overloaded
    # receives file handlers
    # return nodes, ranks and names dicts
    def parse(self, fhs):
        return {}, {}, {}

    def __set_root(self):
        self.__nodes[self.root_node] = self.root_parent
        self.__ranks[self.root_node] = self.root_rank
        self.__names[self.root_node] = self.root_name

    def get_node(self, name):
        # Setup on first use
        if not self.__name_nodes:
            self.__name_nodes = reverse_dict(self.__names)
        if name in self.__name_nodes:
            return self.__name_nodes[name]
        else:
            return [self.unknown_node]

    def get_children(self, node):
        # Setup on first use
        if not self.__node_children:
            self.__node_children = reverse_dict(self.__nodes)
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
        # If is already pre-built and no special subset is required
        if node in self.__lineages and root_node is None and ranks is None:
            return self.__lineages[node]
        else:
            if root_node:
                root_parent = self.get_parent(root_node)
            else:
                root_parent = self.root_parent

            if not ranks:
                ranks = self.fixed_ranks

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
            else:
                # Full lineage
                while n not in [root_parent, self.unknown_node]:
                    lin.append(n)
                    n = self.get_parent(n)
                lin = lin[::-1]

            # If first element of lineage is the tree root parent it could not find the defined root
            # If the last node is unknown, tree is invalid (no connection to root)
            if lin[0] == self.root_parent or n == self.unknown_node:
                return None
            else:
                return lin

    def stats(self):
        s = {}
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

    def check_consistency(self):
        orphan_nodes = []
        for node in self.__nodes:
            if not self.get_lineage(node):
                orphan_nodes.append(node)
        return None

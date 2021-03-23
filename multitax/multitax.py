from .utils import open_files, download_files, close_files, check_file, check_no_file, check_dir, reverse_dict


class MultiTax(object):

    version = "0.1.0"

    _urls = []
    _root_node = "1"

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
                 build_lineages: bool=False,
                 build_name_nodes: bool=False,
                 build_node_children: bool=False):

        if files:
            if isinstance(files, str):
                files = [files]
            for file in files:
                check_file(file)

        if output_prefix:
            check_dir(output_prefix)

        self.root_node = root_node if root_node else self._root_node
        self.root_parent = root_parent
        self.root_name = root_name
        self.root_rank = root_rank
        self.unknown_node = unknown_node
        self.unknown_name = unknown_name
        self.unknown_rank = unknown_rank

        # Main structures
        self.__nodes = {}
        self.__ranks = {}
        self.__names = {}
        self.__lineages = {}
        self.__name_nodes = {}
        self.__node_children = {}

        # Open/Download/Write files
        if files:
            fhs = open_files(files)
        else:
            fhs = download_files(urls=urls if urls else self._urls,
                                 output_prefix=output_prefix)
        # Parse taxonomy
        self.__nodes, self.__ranks, self.__names = self.parse(fhs)
        close_files(fhs)

        # Save sources for stats (files or urls)
        self.sources = list(fhs.keys())

        # Set root node in the tree
        self.__set_root()

        # build auxiliary structures
        if build_name_nodes:
            self.__name_nodes = reverse_dict(self.__names)
        if build_node_children:
            self.__node_children = reverse_dict(self.__nodes)
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
            return []

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

    def get_leaves(self, node):
        # recursive function to get leaf nodes
        leaves = []
        children = self.get_children(node)
        if not children:
            return [node]
        for child in children:
            leaves.extend(self.get_leaves(child))
        return leaves

    def get_parent_rank(self, node, rank):
        while node not in [self.root_parent, self.unknown_node]:
            if self.get_rank(node) == rank:
                return node
            node = self.get_parent(node)
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
                return []
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

    def filter(self, nodes: list, desc: bool=False):
        if isinstance(nodes, str):
            nodes = [nodes]

        # Keep track of nodes to be filtered out
        filtered_nodes = set(self.__nodes)
        # Always keep root
        filtered_nodes.discard(self.root_node)

        if desc:
            # Keep descendants of the given nodes
            for node in nodes:
                # For each leaf of the selected nodes
                for leaf in self.get_leaves(node):
                    # Build lineage of each leaf up-to node itself
                    for n in self.get_lineage(leaf, root_node=node):
                        # Discard nodes from set to be kept
                        filtered_nodes.discard(n)
                # Link node to root
                self.__nodes[node] = self.root_node
        else:
            # Keep ancestors of the given nodes (full lineage up-to root)
            for node in nodes:
                for n in self.get_lineage(node):
                    # Discard nodes from set to be kept
                    filtered_nodes.discard(n)

        # Filter nodes
        for node in filtered_nodes:
            del self.__nodes[node]
            del self.__names[node]
            del self.__ranks[node]
        # Reset data structures
        self.__lineages = {}
        self.__name_nodes = {}
        self.__node_children = {}

    def write(self, output_file, cols: list=["node", "parent", "rank", "name"], sep: str="\t", lineage_sep: str="|", ranks: list=None, gz: bool=False):
        import gzip
        if gz:
            output_file = output_file if output_file.endswith(".gz") else output_file + ".gz"
            check_no_file(output_file)
            outf = gzip.open(output_file, "wt")
        else:
            check_no_file(output_file)
            outf = open(output_file, "w")

        write_field = {"node": lambda node: node,
                       "latest": self.get_latest,
                       "parent": self.get_parent,
                       "rank": self.get_rank,
                       "name": self.get_name,
                       "children": lambda node: lineage_sep.join(self.get_children(node)),
                       "lineage": lambda node: lineage_sep.join(self.get_lineage(node, ranks=ranks)),
                       "rank_lineage": lambda node: lineage_sep.join(self.get_rank_lineage(node, ranks=ranks)),
                       "name_lineage": lambda node: lineage_sep.join(self.get_name_lineage(node, ranks=ranks))}

        for c in cols:
            if c not in write_field:
                raise ValueError(c + " is not a a valid field: " + ",".join(write_field))

        for node in self.__nodes:
            print(*[write_field[c](node) for c in cols], sep=sep, end="\n", file=outf)

        outf.close()

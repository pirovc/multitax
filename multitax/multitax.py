from .utils import open_files, download_files, close_files, check_file, check_no_file, check_dir, reverse_dict


class MultiTax(object):

    version = "0.1.0"

    _default_urls = []
    _default_root_node = "1"

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
                 build_name_nodes: bool=False,
                 build_node_children: bool=False,
                 build_rank_nodes: bool=False):
        """
        Constructor of the class

        Parameters:
        * **files** ***[str, list]***: One or more local files to parse
        * **urls** ***[str, list]***: One or more urls to download and parse
        * **output_prefix** ***[str]***: Directory to write downloaded files
        * **root_node** ***[str]***: 
        * **root_parent** ***[str]***: 
        * **root_name** ***[str]***: 
        * **root_rank** ***[str]***: 
        * **unknown_node** ***[str]***: 
        * **unknown_name** ***[str]***: 
        * **unknown_rank** ***[str]***: 
        * **build_node_children** ***[bool]***: 
        * **build_name_nodes** ***[bool]***: 
        * **build_rank_nodes** ***[bool]***: 
     
        Examples:

            # Downloads default GTDB taxonomy
            tax = GtdbTx()

        """
        if files:
            if isinstance(files, str):
                files = [files]
            for file in files:
                check_file(file)

        if output_prefix:
            check_dir(output_prefix)

        self.root_parent = root_parent
        self.root_name = root_name
        self.root_rank = root_rank
        self.unknown_node = unknown_node
        self.unknown_name = unknown_name
        self.unknown_rank = unknown_rank

        # Main structures
        self._nodes = {}
        self._ranks = {}
        self._names = {}
        self._lineages = {}
        self._name_nodes = {}
        self._node_children = {}
        self._rank_nodes = {}

        # Open/Download/Write files
        if files:
            fhs = open_files(files)
        else:
            fhs = download_files(urls=urls if urls else self._default_urls,
                                 output_prefix=output_prefix)
        # Parse taxonomy
        self._nodes, self._ranks, self._names = self._parse(fhs)

        # Save sources for stats (files or urls)
        self.sources = list(fhs.keys())

        close_files(fhs)

        # Set root node
        self._set_root(custom_root_node=root_node if root_node else None)

        # build auxiliary structures
        if build_node_children:
            self._node_children = reverse_dict(self._nodes)
        if build_name_nodes:
            self._name_nodes = reverse_dict(self._names)
        if build_rank_nodes:
            self._rank_nodes = reverse_dict(self._ranks)

    def _parse(self, fhs):
        """
        main function to be overloaded
        receives a dictionary with {"url/file": file handler}
        return nodes, ranks and names dicts
        """
        return {}, {}, {}

    def _set_root(self, custom_root_node: str=None):
        """
        Set root node define by each class default (_default_root_node) or custom
        """
        if custom_root_node:
            self.root_node = custom_root_node
            # If custom root node is defined, keep only its descendants
            self.filter(custom_root_node, desc=True)
        else:
            self.root_node = self._default_root_node

        # Define root nodes
        self._nodes[self.root_node] = self.root_parent
        self._ranks[self.root_node] = self.root_rank
        self._names[self.root_node] = self.root_name

    def children(self, node):
        """
        Return list of children of a given node
        """
        # Setup on first use
        if not self._node_children:
            self._node_children = reverse_dict(self._nodes)
        if node in self._node_children:
            return self._node_children[node]
        else:
            return []

    def search_name(self, text):
        """
        Return list of nodes containing a certain text
        """
        # Setup on first use
        if not self._name_nodes:
            self._name_nodes = reverse_dict(self._names)

        matching_nodes = []
        for name in self._name_nodes:
            if text in name:
                matching_nodes.extend(self._name_nodes[name])
        return matching_nodes

    def nodes_name(self, name):
        """
        Return list of nodes of a given name
        """
        # Setup on first use
        if not self._name_nodes:
            self._name_nodes = reverse_dict(self._names)
        if name in self._name_nodes:
            return self._name_nodes[name]
        else:
            return []

    def nodes_rank(self, rank):
        """
        Return list of nodes of a given rank
        """
        # Setup on first use
        if not self._rank_nodes:
            self._rank_nodes = reverse_dict(self._ranks)
        if rank in self._rank_nodes:
            return self._rank_nodes[rank]
        else:
            return []

    def parent(self, node):
        """
        Return parent node of a given node
        """
        if node in self._nodes:
            return self._nodes[node]
        else:
            return self.unknown_node

    def rank(self, node):
        """
        Return rank related to the node
        """
        if node in self._ranks:
            return self._ranks[node]
        else:
            return self.unknown_rank

    def name(self, node):
        """
        Return name related to the node
        """
        if node in self._names:
            return self._names[node]
        else:
            return self.unknown_name

    def latest(self, node):
        """
        Get latest version of node in the taxonomy. If node is already the latests, returns itself.
        Mainly used for accessing NCBI (merged.dmp) and OTT (forwards.tsv)
        """
        if node in self._nodes:
            return node
        else:
            return self.unknown_node

    def leaves(self, node):
        """
        Recursive function returning leaf nodes
        """
        leaves = []
        children = self.children(node)
        if not children:
            return [node]
        for child in children:
            leaves.extend(self.leaves(child))
        return leaves

    def lineage(self, node: str, root_node: str=None, ranks: list=None):
        """
        Iterate over taxonomic tree and return node lineage
        Central function iterating the tree structure
        """
        # If lineages were pre-built and no special subset is required
        if node in self._lineages:
            return self._lineages[node]
        else:
            # Define alternative root parent if provided
            root_parent = self.parent(root_node) if root_node else self.root_parent

            lin = []
            n = node
            if ranks:
                # Fixed length lineage
                lin = [self.unknown_node] * len(ranks)
                while n not in [root_parent, self.unknown_node]:
                    r = self.rank(n)
                    if r in ranks:
                        lin[ranks.index(r)] = n
                    n = self.parent(n)
            else:
                # Full lineage
                while n not in [root_parent, self.unknown_node]:
                    lin.append(n)
                    n = self.parent(n)
                lin = lin[::-1]

            # lin[0] == self.root_parent: it could not find the defined/default root
            # n == self.unknown_node:     tree is invalid (no connection to root)
            if lin[0] == self.root_parent or n == self.unknown_node:
                return []
            else:
                return lin

    def rank_lineage(self, node: str, root_node: str=None, ranks: list=None):
        """
        Return lineage of ranks.
        """
        return list(map(self.rank,
                        self.lineage(node=node,
                                     root_node=root_node,
                                     ranks=ranks)))

    def name_lineage(self, node: str, root_node: str=None, ranks: list=None):
        """
        Return lineage of names.
        """
        return list(map(self.name,
                        self.lineage(node=node,
                                     root_node=root_node,
                                     ranks=ranks)))

    def parent_rank(self, node, rank):
        """
        Return parent node of the specified rank.
        """
        return self.lineage(node=node, ranks=[rank])[0]

    def stats(self):
        """
        General stats of the loaded taxonomy.
        """
        s = {}
        s["nodes"] = len(self._nodes)
        s["ranks"] = len(self._ranks)
        s["names"] = len(self._names)
        unique_ranks = set(self._ranks.values())
        s["unique_ranks"] = len(set(self._ranks.values()))
        for ur in unique_ranks:
            s[("nodes", ur)] = list(self._ranks.values()).count(ur)
        return s

    def build_lineages(self, root_node: str=None, ranks: list=None):
        """
        Store lineages in memory for faster access
        """
        self.clear_lineages()
        for node in self._nodes:
            self._lineages[node] = self.lineage(node=node, root_node=root_node, ranks=ranks)

    def clear_lineages(self):
        """
        Clear pre-built lineages.
        """
        self._lineages = {}

    def check_consistency(self):
        """
        Check if loaded taxonomy is consistent. If not, it will return a list of orphan nodes.
        """
        orphan_nodes = []
        for node in self._nodes:
            if not self.lineage(node):
                orphan_nodes.append(node)
        if orphan_nodes:
            return orphan_nodes
        else:
            return None

    def filter(self, nodes: list, desc: bool=False):
        """
        Filter nodes from the taxonomy. By default keep all ancestors of requested nodes.
        If desc=True, keep all descendants instead.
        """
        if isinstance(nodes, str):
            nodes = [nodes]

        # Keep track of nodes to be filtered out
        filtered_nodes = set(self._nodes)
        # Always keep root
        filtered_nodes.discard(self.root_node)

        if desc:
            # Keep descendants of the given nodes
            for node in nodes:
                # For each leaf of the selected nodes
                for leaf in self.leaves(node):
                    # Build lineage of each leaf up-to node itself
                    for n in self.lineage(leaf, root_node=node):
                        # Discard nodes from set to be kept
                        filtered_nodes.discard(n)
                # Link node to root
                self._nodes[node] = self.root_node
        else:
            # Keep ancestors of the given nodes (full lineage up-to root)
            for node in nodes:
                for n in self.lineage(node):
                    # Discard nodes from set to be kept
                    filtered_nodes.discard(n)

        # Filter nodes
        for node in filtered_nodes:
            del self._nodes[node]
            del self._names[node]
            del self._ranks[node]
        # Reset data structures
        self._lineages = {}
        self._name_nodes = {}
        self._node_children = {}

    def write(self, output_file, cols: list=["node", "parent", "rank", "name"], sep: str="\t", lineage_sep: str="|", ranks: list=None, gz: bool=False):
        """
        Write taxonomy to a file.
        cols can be: "node", "latest", "parent", "rank", "name", "leaves", "children", "lineage", "rank_lineage", "name_lineage
        Default cols: "node", "parent", "rank", "name"
        """
        import gzip
        if gz:
            output_file = output_file if output_file.endswith(".gz") else output_file + ".gz"
            check_no_file(output_file)
            outf = gzip.open(output_file, "wt")
        else:
            check_no_file(output_file)
            outf = open(output_file, "w")

        write_field = {"node": lambda node: node,
                       "latest": self.latest,
                       "parent": self.parent,
                       "rank": self.rank,
                       "name": self.name,
                       "leaves": lambda node: lineage_sep.join(self.leaves(node)),
                       "children": lambda node: lineage_sep.join(self.children(node)),
                       "lineage": lambda node: lineage_sep.join(self.lineage(node, ranks=ranks)),
                       "rank_lineage": lambda node: lineage_sep.join(self.rank_lineage(node, ranks=ranks)),
                       "name_lineage": lambda node: lineage_sep.join(self.name_lineage(node, ranks=ranks))}

        for c in cols:
            if c not in write_field:
                raise ValueError(c + " is not a a valid field: " + ",".join(write_field))

        for node in self._nodes:
            print(*[write_field[c](node) for c in cols], sep=sep, end="\n", file=outf)

        outf.close()

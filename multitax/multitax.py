from .utils import open_files, download_files, close_files, check_file, check_no_file, check_dir, reverse_dict
from collections import Counter

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
        Main constructor of MultiTax and sub-classes

        Parameters:
        * **files** *[str, list]*: One or more local files to parse
        * **urls** *[str, list]*: One or more urls to download and parse
        * **output_prefix** *[str]*: Directory to write downloaded files
        * **root_node** *[str]*: Define an alternative root node (has to exist in the taxonomy)
        * **root_parent** *[str]*: Define an alternative root parent
        * **root_name** *[str]*: Define an alternative root name
        * **root_rank** *[str]*: Define an alternative root rank
        * **unknown_node** *[str]*: Define a default return value for unknow/undefined nodes
        * **unknown_name** *[str]*: Define a default return value for unknow/undefined names
        * **unknown_rank** *[str]*: Define a default return value for unknow/undefined ranks
        * **build_node_children** *[bool]*: Pre-build node,children dict (otherwise it will be created on first use)
        * **build_name_nodes** *[bool]*: Pre-build name,nodes dict (otherwise it will be created on first use)
        * **build_rank_nodes** *[bool]*: Pre-build rank,nodes dict (otherwise it will be created on first use)
     
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

        # Set undefined values
        self.unknown_node = unknown_node
        self.unknown_name = unknown_name
        self.unknown_rank = unknown_rank

        # Set root values
        self.root_parent = root_parent
        self.root_name = root_name
        self.root_rank = root_rank
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
        Return list of nodes which containing a certain text in their names
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
        parent = self.lineage(node=node, ranks=[rank])
        return parent[0] if parent else None

    def stats(self):
        """
        General stats of the taxonomic tree

        Paramenters: None

        Returns:

        * **[dict]** with total counts "nodes", "ranks", "names", "leaves" and rank specific counts "ranked_nodes", "ranked_leaves" with total of counts for each rank
        
        Example:

            from pprint import pprint
            from multitax import GtdbTx
            tax = GtdbTx()

            pprint(tax.stats())
            {'leaves': 30238,
             'names': 42739,
             'nodes': 42739,
             'ranked_leaves': Counter({'species': 30238}),
             'ranked_nodes': Counter({'species': 30238,
                                      'genus': 8778,
                                      'family': 2323,
                                      'order': 930,
                                      'class': 337,
                                      'phylum': 131,
                                      'domain': 1,
                                      'root': 1}),
             'ranks': 42739}
        """
        s = {}
        s["nodes"] = len(self._nodes)
        s["ranks"] = len(self._ranks)
        s["names"] = len(self._names)
        all_leaves = self.leaves(self.root_node)
        s["leaves"] = len(all_leaves)
        s["ranked_nodes"] = Counter(self._ranks.values())
        s["ranked_leaves"] = Counter(map(self.rank, all_leaves))

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
        Filter taxonomy to selected nodes.
        By default keep all the ancestors of the given nodes.
        If desc=True, keep all descendants instead.
        It will delete pre-build lineages.

        Parameters:
        * ...

        Returns: None

        Example:

            from multitax import GtdbTx
            tax = GtdbTx()

            tax.lineage('s__Enterovibrio marina')
            # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Vibrionaceae', 'g__Enterovibrio', 's__Enterovibrio marina']

            # Keep only ancestors of 'g__Enterovibrio'
            tax.filter('g__Enterovibrio')
            tax.stats()
            # {'nodes': 7, 'ranks': 7, 'names': 7, 'unique_ranks': 7, ('nodes', 'class'): 1, ('nodes', 'root'): 1, ('nodes', 'phylum'): 1, ('nodes', 'domain'): 1, ('nodes', 'genus'): 1, ('nodes', 'order'): 1, ('nodes', 'family'): 1}

            # Reload taxonomy
            tax = GtdbTx()

            # Keep only descendants of 'g__Enterovibrio'
            tax.filter('g__Enterovibrio', desc=True)
            tax.stats()
            #{'nodes': 17, 'ranks': 17, 'names': 17, 'unique_ranks': 3, ('nodes', 'root'): 1, ('nodes', 'species'): 15, ('nodes', 'genus'): 1}

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
        self._node_children = {}
        self._name_nodes = {}
        self._rank_nodes = {}

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

from .utils import *
from collections import Counter


class MultiTax(object):

    version = "1.3.0"

    _default_urls = []
    _default_root_node = "1"

    def __init__(self,
                 files: list = None,
                 urls: list = None,
                 output_prefix: str = None,
                 root_node: str = None,
                 root_parent: str = "0",
                 root_name: str = None,
                 root_rank: str = None,
                 undefined_node: str = None,
                 undefined_name: str = None,
                 undefined_rank: str = None,
                 build_name_nodes: bool = False,
                 build_node_children: bool = False,
                 build_rank_nodes: bool = False,
                 extended_names: bool = False):
        """
        Main constructor of MultiTax and sub-classes

        Parameters:
        * **files** *[str, list]*: One or more local files to parse.
        * **urls** *[str, list]*: One or more urls to download and parse.
        * **output_prefix** *[str]*: Directory to write downloaded files.
        * **root_node** *[str]*: Define an alternative root node.
        * **root_parent** *[str]*: Define the root parent node identifier.
        * **root_name** *[str]*: Define an alternative root name. Set to None to use original name.
        * **root_rank** *[str]*: Define an alternative root rank. Set to None to use original name.
        * **undefined_node** *[str]*: Define a default return value for undefined nodes.
        * **undefined_name** *[str]*: Define a default return value for undefined names.
        * **undefined_rank** *[str]*: Define a default return value for undefined ranks.
        * **build_node_children** *[bool]*: Build node,children dict (otherwise it will be created on first use).
        * **build_name_nodes** *[bool]*: Build name,nodes dict (otherwise it will be created on first use).
        * **build_rank_nodes** *[bool]*: Build rank,nodes dict (otherwise it will be created on first use).
        * **extended_names** *[bool]*: Parse extended names if available.

        Example:

            tax_ncbi = NcbiTx()
            tax_gtdb = GtdbTx(files=["file1.gz", "file2.txt"])
            tax_silva = SilvaTx(urls=["https://www.arb-silva.de/fileadmin/silva_databases/current/Exports/taxonomy/tax_slv_lsu_138.1.txt.gz"])
            tax_ott = OttTx(root_node="844192")
            tax_gg = GreengenesTx(output_prefix="save/to/prefix_")
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
        # Aux. structures
        self._lineages = {}
        self._name_nodes = {}
        self._node_children = {}
        self._rank_nodes = {}
        self._translated_nodes = {}

        # Store source of tax files (url or file)
        self.sources = []

        # Open/Download/Write files
        fhs = {}
        if files:
            fhs = open_files(files)
        elif urls or self._default_urls:
            fhs = download_files(urls=urls if urls else self._default_urls,
                                 output_prefix=output_prefix,
                                 retry_attempts=3)

        if fhs:
            # Parse taxonomy
            self._nodes, self._ranks, self._names = self._parse(
                fhs, extended_names=extended_names)
            close_files(fhs)
            # Save sources for stats (files or urls)
            self.sources = list(fhs.keys())

        # Set undefined values
        self.undefined_node = undefined_node
        self.undefined_name = undefined_name
        self.undefined_rank = undefined_rank

        # Set root values
        self._set_root_node(root=root_node if root_node else self._default_root_node,
                            parent=root_parent, name=root_name, rank=root_rank)

        # build auxiliary structures
        if build_node_children:
            self._node_children = reverse_dict(self._nodes)
        if build_name_nodes:
            self._name_nodes = reverse_dict(self._names)
        if build_rank_nodes:
            self._rank_nodes = reverse_dict(self._ranks)

        self.check_consistency()

    def _exact_name(self, text: str, names: dict):
        """
        Returns list of nodes of a given exact name (case sensitive).
        """
        if text in names:
            return names[text]
        else:
            return []

    def _parse(self, fhs: dict):
        """
        main function to be overloaded
        receives a dictionary with {"url/file": file handler}
        return nodes, ranks and names dicts
        """
        return {}, {}, {}

    def _partial_name(self, text: str, names: dict):
        """
        Searches names containing a certain text (case sensitive) and return their respective nodes.
        """
        matching_nodes = set()
        for name in names:
            if text in name:
                matching_nodes.update(names[name])
        return list(matching_nodes)

    def _recurse_leaves(self, node: str):
        """
        Recursive function returning leaf nodes
        """
        children = self.children(node)
        if not children:
            return [node]
        leaves = []
        for child in children:
            leaves.extend(self._recurse_leaves(child))
        return leaves

    def _remove(self, node: str):
        """
        Removes node from taxonomy, no checking, for internal use
        """
        del self._nodes[node]
        if node in self._names:
            del self._names[node]
        if node in self._ranks:
            del self._ranks[node]

    def _reset_aux_data(self):
        """
        Reset aux. data structures
        """
        self._lineages = {}
        self._name_nodes = {}
        self._node_children = {}
        self._rank_nodes = {}
        self._translated_nodes = {}

    def _set_root_node(self, root: str, parent: str, name: str, rank: str):
        """
        Set root node of the tree.
        The files are parsed based on the self._default_root_node for each class
        A user-defined root node can be:
        1) internal: will filter the tree acodingly and delete the default root_node
        2) external: will add node and link to the default
        """

        # Set parent/root with defaults
        self.root_parent = parent
        self.root_node = self._default_root_node
        self._nodes[self.root_node] = self.root_parent

        # Default root node is the top by definition
        if root != self._default_root_node:
            if root in self._nodes:
                # Not default but exists on tree, filter only descendants
                self.filter(root, desc=True)
                # Remove entry for _default_root_node
                self._remove(self._default_root_node)
            else:
                # Not on tree, link default node with new root
                self._nodes[self._default_root_node] = root
            # Change root to user defined
            self.root_node = root
            # Set/Update new root node parent link
            self._nodes[self.root_node] = self.root_parent

        # User-defined rank/name.
        # If provided, insert manually,
        # If None, check if is in the tree (defined in the given tax)
        #    otherwise insert default "root"
        if name:
            self._names[self.root_node] = name
        elif self.root_node not in self._names:
            self._names[self.root_node] = "root"
        # Set static name
        self.root_name = self._names[self.root_node]

        if rank:
            self._ranks[self.root_node] = rank
        elif self.root_node not in self._ranks:
            self._ranks[self.root_node] = "root"
        # Set static rank
        self.root_rank = self._ranks[self.root_node]

    def add(self, node: str, parent: str, name: str = None, rank: str = None):
        """
        Add node to taxonomy.
        Deletes built lineages and translations.
        """
        if parent not in self._nodes:
            raise ValueError("Parent node [" + parent + "] not found.")
        elif node in self._nodes:
            raise ValueError("Node [" + node + "] already present.")
        
        self._nodes[node] = parent
        self._names[node] = name if name is not None else self.undefined_name
        self._ranks[node] = rank if rank is not None else self.undefined_rank
        self._reset_aux_data()

    def build_lineages(self, root_node: str = None, ranks: list = None):
        """
        Stores lineages in memory for faster access.
        It is valid for lineage(), rank_lineage() and name_lineage().
        If keyword arguments (root_node, ranks) are used in those functions stored lineages are not used.

        Returns: None
        """
        self.clear_lineages()
        for node in self._nodes:
            self._lineages[node] = self.lineage(
                node=node, root_node=root_node, ranks=ranks)

    def build_translation(self, tax, files: list = None, urls: list = None):
        """
        Create a translation of current taxonomy to another

        Parameters:

        * **tax** [MultiTax]: A target taxonomy to be translated to.
        * **files** *[str, list]*: One or more local files to parse.
        * **urls** *[str, list]*: One or more urls to download and parse.

        Example:

            from multitax import GtdbTx, NcbiTx
            gtdb_tax = GtdbTx()
            ncbi_tax = NcbiTx()

            # Automatically download translation files
            gtdb_tax.build_translation(ncbi_tax)
            gtdb_tax.translate("g__Escherichia")
                {'1301', '547', '561', '570', '590', '620'}

            # Using local files (NCBI <-> GTDB)
            ncbi_tax.build_translation(gtdb_tax, files=["ar53_metadata.tar.gz", "bac120_metadata.tar.gz"])
            ncbi_tax.translate("620")
                {'g__Escherichia', 'g__Proteus', 'g__Serratia'}
        """
        if files:
            if isinstance(files, str):
                files = [files]
            for file in files:
                check_file(file)

        self._translated_nodes = self._build_translation(tax, files, urls)

    def children(self, node: str):
        """
        Returns list of direct children nodes of a given node.
        """
        # Setup on first use
        if not self._node_children:
            self._node_children = reverse_dict(self._nodes)
        if node in self._node_children:
            return self._node_children[node]
        else:
            return []

    def check_consistency(self):
        """
        Checks consistency of the tree

        Returns: raise an Exception otherwise None
        """
        if self.root_node not in self._nodes:
            raise ValueError("Root node [" + self.root_node + "] not found.")
        if self.root_parent in self._nodes:
            raise ValueError(
                "Root parent [" + self.root_parent + "] found but should not be on tree.")
        if self.undefined_node in self._nodes:
            raise ValueError(
                "Undefined node [" + self.undefined_node + "] found but should not be on tree.")

        # Difference between values and keys should be only root_parent
        lost_nodes = set(self._nodes.values()).difference(self._nodes)
        if self.root_parent not in lost_nodes:
            raise ValueError(
                "Root parent [" + self.root_parent + "] not properly defined.")
        # Remove root_parent from lost nodes to report only missing
        lost_nodes.remove(self.root_parent)
        if len(lost_nodes) > 0:
            raise ValueError("Parent nodes missing: " + ",".join(lost_nodes))

        return None

    def clear_lineages(self):
        """
        Clear built lineages.

        Returns: None
        """
        self._lineages = {}

    def closest_parent(self, node: str, ranks: str):
        """
        Returns the closest parent node based on a defined list of ranks
        """
        # Rank of node is already on the list
        if self.rank(node) in ranks:
            return node
        else:
            # check lineage from back to front until find a valid node
            for n in self.lineage(node, ranks=ranks)[::-1]:
                if n != self.undefined_node:
                    return n
        # nothing found
        return self.undefined_node

    def filter(self, nodes: list, desc: bool = False):
        """
        Filters taxonomy given a list of nodes.
        By default keep all the ancestors of the given nodes.
        If desc=True, keep all descendants instead.
        Deletes built lineages and translations.

        Example:

            from multitax import GtdbTx
            tax = GtdbTx()

            tax.lineage('s__Enterovibrio marina')
            # ['1', 'd__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria', 'o__Enterobacterales', 'f__Vibrionaceae', 'g__Enterovibrio', 's__Enterovibrio marina']
            # Keep only ancestors of 'g__Enterovibrio'
            tax.filter('g__Enterovibrio')

            # Reload taxonomy
            tax = GtdbTx()
            # Keep only descendants of 'g__Enterovibrio'
            tax.filter('g__Enterovibrio', desc=True)
        """
        if isinstance(nodes, str):
            nodes = [nodes]

        # Cannot filter root node
        if self.root_node in nodes:
            raise ValueError("Root node [" + self.root_node + "] cannot be filtered.")

        # Keep track of nodes to be filtered out
        filtered_nodes = set(self._nodes)
        # Always keep root
        filtered_nodes.discard(self.root_node)

        if desc:
            # Keep descendants of the given nodes
            for node in nodes:
                # Check if node exists
                if node in filtered_nodes:
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
                # ranks=[] in case build_lineages() was used with specific ranks
                for n in self.lineage(node, ranks=[]):
                    # Discard nodes from set to be kept
                    filtered_nodes.discard(n)

        # Delete filtered nodes
        for node in filtered_nodes:
            self._remove(node)

        # Delete aux. data structures
        self._reset_aux_data()

        self.check_consistency()

    def latest(self, node: str):
        """
        Returns latest/updated version of a given node.
        If node is already the latests, returns itself.
        Mainly used for NCBI (merged.dmp) and OTT (forwards.tsv)
        """
        if node in self._nodes:
            return node
        else:
            return self.undefined_node

    def leaves(self, node: str = None):
        """
        Returns a list of leaf nodes of a given node.
        """
        if node is None or node == self.root_node:
            # Leaves are nodes not contained in _nodes.values() ("parents")
            return list(set(self._nodes).difference(self._nodes.values()))
        elif node in self._nodes:
            return self._recurse_leaves(node)
        else:
            return []

    def lineage(self, node: str, root_node: str = None, ranks: list = None):
        """
        Returns a list with the lineage of a given node.
        If ranks is provided, returns only nodes annotated with such ranks.
        If root_node is provided, use it instead of default root of tree.
        """
        # If lineages were built with build_lineages() with matching params
        if node in self._lineages and root_node is None and ranks is None:
            return self._lineages[node]
        else:
            if not root_node:
                root_node = self.root_node

            n = node
            if ranks:
                # Fixed length lineage
                lin = [self.undefined_node] * len(ranks)
                # Loop until end of the tree (in case chosen root is not on lineage)
                while n != self.undefined_node:
                    r = self.rank(n)
                    if r in ranks:
                        lin[ranks.index(r)] = n
                    # If node is root, break (after adding)
                    if n == root_node:
                        break
                    n = self.parent(n)
            else:
                # Full lineage
                lin = []
                # Loop until end of the tree (in case chosen root is not on lineage)
                while n != self.undefined_node:
                    lin.append(n)
                    # If node is root, break (after adding)
                    if n == root_node:
                        break
                    n = self.parent(n)
                # Reverse order
                lin = lin[::-1]

            # last iteration node (n) != root_node: didn't find the root, invalid lineage
            if n != root_node:
                return []
            else:
                return lin

    def name(self, node: str):
        """
        Returns name of a given node.
        """
        if node in self._names:
            return self._names[node]
        else:
            return self.undefined_name

    def name_lineage(self, node: str, root_node: str = None, ranks: list = None):
        """
        Returns a list with the name lineage of a given node.
        """
        return list(map(self.name,
                        self.lineage(node=node,
                                     root_node=root_node,
                                     ranks=ranks)))

    def nodes_rank(self, rank: str):
        """
        Returns list of nodes of a given rank.
        """
        # Setup on first use
        if not self._rank_nodes:
            self._rank_nodes = reverse_dict(self._ranks)
        if rank in self._rank_nodes:
            return self._rank_nodes[rank]
        else:
            return []

    def parent(self, node: str):
        """
        Returns the direct parent node of a given node.
        """
        if node in self._nodes:
            return self._nodes[node]
        else:
            return self.undefined_node

    def parent_rank(self, node: str, rank: str):
        """
        Returns the parent node of a given rank in the specified rank.
        """
        parent = self.lineage(node=node, ranks=[rank])
        return parent[0] if parent else self.undefined_node

    def prune(self, nodes: list):
        """
        Prunes branches of the tree under the given nodes.
        Deletes built lineages and translations.
        """

        if isinstance(nodes, str):
            nodes = [nodes]

        del_nodes = set()
        for node in nodes:
            if node not in self._nodes:
                raise ValueError("Node [" + node + "] not found.")
            for leaf in self.leaves(node):
                for n in self.lineage(leaf, root_node=node)[1:]:
                    del_nodes.add(n)

        for n in del_nodes:
            self._remove(n)

        self._reset_aux_data()

    def rank(self, node: str):
        """
        Returns the rank of a given node.
        """
        if node in self._ranks:
            return self._ranks[node]
        else:
            return self.undefined_rank

    def rank_lineage(self, node: str, root_node: str = None, ranks: list = None):
        """
        Returns a list with the rank lineage of a given node.
        """
        return list(map(self.rank,
                        self.lineage(node=node,
                                     root_node=root_node,
                                     ranks=ranks)))

    def remove(self, node: str, check_consistency: bool = False):
        """
        Removes node from taxonomy. Can break the tree if a parent node is removed. To remove a certain branch, use prune.
        Running check consistency after removing a node is recommended.
        Deletes built lineages and translations.
        """
        if node not in self._nodes:
            raise ValueError("Node [" + node + "] not found.")
        self._remove(node)
        self._reset_aux_data()
        if check_consistency:
            self.check_consistency()

    def search_name(self, text: str, rank: str = None, exact: bool = True):
        """
        Search node by exact or partial name

        Parameters:
        * **text** *[str]*: Text to search.
        * **rank** *[str]*: Filter results by rank.
        * **exact** *[bool]*: Exact or partial name search (both case sensitive).

        Returns: list of matching nodes
        """
        # Setup on first use
        if not self._name_nodes:
            self._name_nodes = reverse_dict(self._names)

        if exact:
            ret = self._exact_name(text, self._name_nodes)
        else:
            ret = self._partial_name(text, self._name_nodes)

        # Only return nodes of chosen rank
        if rank:
            return filter_function(ret, self.rank, rank)
        else:
            return ret

    def stats(self):
        """
        Returns a dict with general numbers of the taxonomic tree

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

    def translate(self, node: str):
        """
        Returns the translated node from another taxonomy. Translated nodes are generated with the build_translation function.
        """
        if node in self._translated_nodes:
            return self._translated_nodes[node]
        else:
            return []

    def write(self,
              output_file: str,
              cols: list = ["node", "parent", "rank", "name"],
              sep: str = "\t",
              sep_multi: str = "|",
              ranks: list = None,
              gz: bool = False):
        """
        Writes loaded taxonomy to a file.

        Parameters:
        * **cols** *[list]*: Options: "node", "latest", "parent", "rank", "name", "leaves", "children", "lineage", "rank_lineage", "name_lineage"
        * **sep** *[str]*: Separator of fields
        * **sep_multi** *[str]*: Separator of multi-valued fields
        * **ranks** *[list]*: Ranks to report
        * **gz** *[bool]*: Gzip output

        Returns: None
        """
        import gzip
        if gz:
            output_file = output_file if output_file.endswith(
                ".gz") else output_file + ".gz"
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
                       "leaves": lambda node: join_check(self.leaves(node), sep_multi),
                       "children": lambda node: join_check(self.children(node), sep_multi),
                       "lineage": lambda node: join_check(self.lineage(node, ranks=ranks), sep_multi),
                       "rank_lineage": lambda node: join_check(self.rank_lineage(node, ranks=ranks), sep_multi),
                       "name_lineage": lambda node: join_check(self.name_lineage(node, ranks=ranks), sep_multi)}

        for c in cols:
            if c not in write_field:
                raise ValueError(
                    "Field [" + c + "] is not valid. Options: " + ",".join(write_field))

        if ranks:
            for rank in ranks:
                for node in self.nodes_rank(rank):
                    print(*[write_field[c](node)
                            for c in cols], sep=sep, end="\n", file=outf)
        else:
            for node in self._nodes:
                print(*[write_field[c](node)
                        for c in cols], sep=sep, end="\n", file=outf)

        outf.close()

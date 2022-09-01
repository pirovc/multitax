import unittest
from multitax import CustomTx
from multitax.multitax import MultiTax


class TestInit(unittest.TestCase):
    # test data (14 nodes)
    #
    # rank-1 (root)            1 ___________
    #                         / \           \
    # rank-2                2.1 2.2 ______   \
    #                       / \    \      \   \
    # rank-3             3.1  3.2   3.4    \   \
    #                     /   / \     \     \   \
    # rank-4          *4.1 *4.2 *4.3  *4.4  *4.5 *4.6
    #                                 / |
    # rank-5                     *5.1 *5.2
    #
    # names: 1: Node1, 2.1: Node2.1, ...,5.2: Node5.2

    test_file = "tests/multitax/data_minimal/custom_unit_test.tsv.gz"

    def test_default(self):
        """
        test default values on empty init
        """
        # Empty tax
        tax = MultiTax()
        self.assertEqual(tax.root_parent, "0")
        self.assertEqual(tax.root_node, tax._default_root_node)
        self.assertEqual(tax.root_name, "root")
        self.assertEqual(tax.root_rank, "root")

        self.assertEqual(tax._default_urls, [])
        self.assertEqual(tax._default_root_node, "1")
        self.assertEqual(tax._nodes, {tax.root_node: '0'})
        self.assertEqual(tax._names, {tax.root_node: 'root'})
        self.assertEqual(tax._ranks, {tax.root_node: 'root'})
        self.assertEqual(tax._lineages, {})
        self.assertEqual(tax._name_nodes, {})
        self.assertEqual(tax._node_children, {})
        self.assertEqual(tax._rank_nodes, {})

        self.assertEqual(tax.undefined_node, None)
        self.assertEqual(tax.undefined_name, None)
        self.assertEqual(tax.undefined_rank, None)
        self.assertEqual(tax.sources, [])

        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.root_parent, "0")
        self.assertEqual(tax.root_node, tax._default_root_node)
        self.assertEqual(tax.root_name, "Node1")
        self.assertEqual(tax.root_rank, "rank-1")

        self.assertEqual(tax._default_urls, [])
        self.assertEqual(tax._default_root_node, "1")
        self.assertEqual(tax._nodes[tax.root_node], "0")
        self.assertEqual(tax._names[tax.root_node], "Node1")
        self.assertEqual(tax._ranks[tax.root_node], "rank-1")
        self.assertEqual(tax._lineages, {})
        self.assertEqual(tax._name_nodes, {})
        self.assertEqual(tax._node_children, {})
        self.assertEqual(tax._rank_nodes, {})

        self.assertEqual(tax.undefined_node, None)
        self.assertEqual(tax.undefined_name, None)
        self.assertEqual(tax.undefined_rank, None)
        self.assertEqual(tax.sources, [self.test_file])

    def test_root_values(self):
        """
        test init changing root values
        """

        # New root, not on tree
        tax = MultiTax(root_node="root_n", root_parent="root_p", root_name="newRootName", root_rank="newRootRank")
        self.assertEqual(tax.root_node, "root_n")
        self.assertEqual(tax.root_parent, "root_p")
        # Create new root node and link old default (1) {"root_n": "root_p", "1": "root_p"}
        self.assertEqual(tax._nodes, {tax.root_node: tax.root_parent, tax._default_root_node: tax.root_node})
        self.assertEqual(tax.root_name, 'newRootName')
        self.assertEqual(tax._names, {tax.root_node: 'newRootName'})
        self.assertEqual(tax.root_rank, 'newRootRank')
        self.assertEqual(tax._ranks, {tax.root_node: 'newRootRank'})

        # Root is a new node not in nodes
        tax = CustomTx(files=self.test_file, root_node="root_n", root_parent="root_p", root_name="newRootName", root_rank="newRootRank")
        self.assertEqual(tax.root_node, "root_n")
        self.assertEqual(tax.root_parent, "root_p")
        self.assertEqual(tax.stats()["nodes"], 15)

        # Create new root node and link old default (1) {"root_n": "root_p", "1": "root_p"}
        self.assertEqual(tax.parent(tax.root_node), tax.root_parent)
        self.assertEqual(tax.name(tax.root_node), 'newRootName')
        self.assertEqual(tax.rank(tax.root_node), 'newRootRank')
        # Default root is linked to new root
        self.assertEqual(tax.parent(tax._default_root_node), tax.root_node)
        self.assertEqual(tax.name(tax._default_root_node), "Node1")
        self.assertEqual(tax.rank(tax._default_root_node), "rank-1")

        # Root is an existing node in nodes, but not default, filter tree under node
        tax = CustomTx(files=self.test_file, root_node="4.4", root_parent="root_p", root_name="newRootName", root_rank="newRootRank")
        self.assertEqual(tax.root_node, "4.4")
        self.assertEqual(tax.root_parent, "root_p")
        self.assertEqual(tax.stats()["nodes"], 3)

        # Create new root node and link old default (1) {"root_n": "root_p", "1": "root_p"}
        self.assertEqual(tax.parent(tax.root_node), tax.root_parent)
        self.assertEqual(tax.name(tax.root_node), 'newRootName')
        self.assertEqual(tax.rank(tax.root_node), 'newRootRank')
        # default root should not exist
        self.assertEqual(tax.parent(tax._default_root_node), tax.undefined_node)
        self.assertEqual(tax.name(tax._default_root_node), tax.undefined_name)
        self.assertEqual(tax.rank(tax._default_root_node), tax.undefined_rank)

    def test_undefined_values(self):
        """
        test init changing undefined values
        """
        tax = MultiTax(undefined_node="unode", undefined_rank="urank", undefined_name="uname")
        self.assertEqual(tax.undefined_node, "unode")
        self.assertEqual(tax.undefined_name, "uname")
        self.assertEqual(tax.undefined_rank, "urank")
        self.assertEqual(tax.parent("XXX"), "unode")
        self.assertEqual(tax.rank("XXX"), "urank")
        self.assertEqual(tax.name("XXX"), "uname")

        tax = CustomTx(files=self.test_file, undefined_node="unode", undefined_rank="urank", undefined_name="uname")
        self.assertEqual(tax.undefined_node, "unode")
        self.assertEqual(tax.undefined_name, "uname")
        self.assertEqual(tax.undefined_rank, "urank")
        self.assertEqual(tax.parent("XXX"), "unode")
        self.assertEqual(tax.rank("XXX"), "urank")
        self.assertEqual(tax.name("XXX"), "uname")

    def test_build_values(self):
        """
        test init changing undefined values
        """
        tax = MultiTax(build_node_children=True, build_name_nodes=True, build_rank_nodes=True)
        self.assertEqual(tax._name_nodes, {tax.name(tax.root_node): [tax.root_node]})
        self.assertEqual(tax._node_children, {tax.root_parent: [tax.root_node]})
        self.assertEqual(tax._rank_nodes, {"root": [tax.root_node]})

        tax = CustomTx(files=self.test_file, build_node_children=True, build_name_nodes=True, build_rank_nodes=True)
        self.assertNotEqual(len(tax._name_nodes), 0)
        self.assertNotEqual(len(tax._node_children), 0)
        self.assertNotEqual(len(tax._rank_nodes), 0)

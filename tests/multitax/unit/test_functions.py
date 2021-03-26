import unittest
import sys

sys.path.append("tests/multitax/")
from utils import setup_dir

from multitax import CustomTx
from multitax.utils import check_file

class TestFunctions(unittest.TestCase):
    # test data
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
    tmp_dir = "tests/multitax/unit/tmp_functions/"

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_children(self):
        """
        test children function
        """
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.children("1"), ["2.1", "2.2", "4.6"])
        self.assertCountEqual(tax.children("2.1"), ["3.1", "3.2"])
        self.assertCountEqual(tax.children("2.2"), ["3.4", "4.5"])
        self.assertCountEqual(tax.children("4.4"), ["5.1", "5.2"])
        self.assertCountEqual(tax.children("5.2"), [])
        self.assertCountEqual(tax.children("XXX"), [])

    def test_search_name(self):
        """
        test search_name function
        """
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.search_name("Node2"), ["2.1", "2.2"])
        self.assertCountEqual(tax.search_name("Node1"), ["1"])
        self.assertCountEqual(tax.search_name("NotThere"), [])

        tax = CustomTx(files=self.test_file, root_name="AnotherRootName")
        self.assertCountEqual(tax.search_name("Node1"), [])
        self.assertCountEqual(tax.search_name("Another"), ["1"])

    def test_nodes_name(self):
        """
        test nodes_name function
        """
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.nodes_name("Node1"), ["1"])
        self.assertCountEqual(tax.nodes_name("Node2.1"), ["2.1"])
        self.assertCountEqual(tax.nodes_name("Node5.2"), ["5.2"])
        self.assertCountEqual(tax.nodes_name("Node2."), [])

    def test_nodes_rank(self):
        """
        test nodes_rank function
        """
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.nodes_rank("rank-1"), ["1"])
        self.assertCountEqual(tax.nodes_rank("rank-4"), ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"])
        self.assertCountEqual(tax.nodes_rank("rank-9999"), [])

    def test_parent(self):
        """
        test parent function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.parent("1"), tax.root_parent)
        self.assertEqual(tax.parent("3.2"), "2.1")
        self.assertEqual(tax.parent("5.2"), "4.4")
        self.assertEqual(tax.parent("PpQqRr"), tax.undefined_node)

        tax = CustomTx(files=self.test_file, undefined_node="NoNode")
        self.assertEqual(tax.parent("ABVCDE"), "NoNode")

    def test_rank(self):
        """
        test rank function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.rank("4.1"), "rank-4")
        self.assertEqual(tax.rank("1"), "rank-1")
        self.assertEqual(tax.rank("5.2"), "rank-5")
        self.assertEqual(tax.rank("what"), tax.undefined_rank)

        tax = CustomTx(files=self.test_file, undefined_rank="NoRank")
        self.assertEqual(tax.rank("ABVCDE"), "NoRank")

    def test_name(self):
        """
        test name function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.name("4.1"), "Node4.1")
        self.assertEqual(tax.name("1"), "Node1")
        self.assertEqual(tax.name("2.2"), "Node2.2")
        self.assertEqual(tax.name("ABVCDE"), tax.undefined_name)

        tax = CustomTx(files=self.test_file, undefined_name="NoName")
        self.assertEqual(tax.name("ABVCDE"), "NoName")

    def test_latest(self):
        """
        test latest function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.latest("4.1"), "4.1")
        self.assertEqual(tax.latest("1"), "1")
        self.assertEqual(tax.latest("4.6"), "4.6")
        self.assertEqual(tax.latest("XxXxXx"), tax.undefined_node)

    def test_leaves(self):
        """
        test leaves function
        """
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.leaves(), ["4.1", "4.2", "4.3", "4.5", "4.6", "5.1", "5.2"])
        self.assertCountEqual(tax.leaves("1"), ["4.1", "4.2", "4.3", "5.1", "5.2", "4.5", "4.6"])
        self.assertCountEqual(tax.leaves("2.2"), ["5.1", "5.2", "4.5"])
        self.assertCountEqual(tax.leaves("4.4"), ["5.1", "5.2"])
        self.assertCountEqual(tax.leaves("5.1"), ["5.1"])
        self.assertCountEqual(tax.leaves("999.999"), [])

    def test_lineage(self):
        """
        test lineage function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.lineage("5.2"), ["1", "2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("3.2"), ["1", "2.1", "3.2"])
        self.assertEqual(tax.lineage("4.6"), ["1", "4.6"])
        self.assertEqual(tax.lineage("1"), ["1"])
        self.assertEqual(tax.lineage("9999"), [])

        # with ranks
        self.assertEqual(tax.lineage("5.2", ranks=["rank-1", "rank-3", "rank-5"]),
                         ["1", "3.4", "5.2"])
        self.assertEqual(tax.lineage("5.2", ranks=["rank-3", "rank-5", "rank-1"]),
                         ["3.4", "5.2", "1"])
        self.assertEqual(tax.lineage("4.5", ranks=["rank-1"]),
                         ["1"])
        self.assertEqual(tax.lineage("3.2", ranks=["rank-4", "rank-5"]),
                         [tax.undefined_node, tax.undefined_node])
        self.assertEqual(tax.lineage("4.5", ranks=["rank-1", "rank-2", "rank-3", "rank-4", "rank-5"]),
                         ["1", "2.2", tax.undefined_node, "4.5", tax.undefined_node])
        self.assertEqual(tax.lineage("4.6", ranks=["xxxx", "yyy"]),
                         [tax.undefined_node, tax.undefined_node])
        # Invalid lineage
        self.assertEqual(tax.lineage("ZZZ", ranks=["xxxx", "yyy"]),
                         [])

        # with root_node
        self.assertEqual(tax.lineage("5.2", root_node="2.2"),
                         ["2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("4.2", root_node="2.1"),
                         ["2.1", "3.2", "4.2"])
        self.assertEqual(tax.lineage("4.5", root_node="2.2"),
                         ["2.2", "4.5"])
        # Invalid lineage
        self.assertEqual(tax.lineage("5.2", root_node="2.1"),
                         [])
        self.assertEqual(tax.lineage("3.1", root_node="4.1"),
                         [])
        self.assertEqual(tax.lineage("XXX", root_node="YYY"),
                         [])

        # with both
        self.assertEqual(tax.lineage("5.2", root_node="2.2", ranks=["rank-3", "rank-4"]),
                         ["3.4", "4.4"])
        self.assertEqual(tax.lineage("5.1", root_node="3.4", ranks=["rank-3", "rank-5"]),
                         ["3.4", "5.1"])
        self.assertEqual(tax.lineage("4.1", root_node="2.1", ranks=["rank-1", "rank-2", "rank-3", "rank-5"]),
                         [tax.undefined_node, "2.1", "3.1", tax.undefined_node])
        self.assertEqual(tax.lineage("4.1", root_node="2.1", ranks=["rank-1", "rank-5"]),
                         [tax.undefined_node, tax.undefined_node])
        self.assertEqual(tax.lineage("4.1", root_node="2.1", ranks=["XXXXX"]),
                         [tax.undefined_node])
        # Invalid lineage
        self.assertEqual(tax.lineage("4.1", root_node="5.1", ranks=["rank-1", "rank-2", "rank-3", "rank-5"]),
                         [])
        self.assertEqual(tax.lineage("XXXX", root_node="2.2", ranks=["rank-3", "rank-4"]),
                         [])

    def test_rank_lineage(self):
        """
        test rank_lineage function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.rank_lineage("5.2"), ["rank-1", "rank-2", "rank-3", "rank-4", "rank-5"])
        self.assertEqual(tax.rank_lineage("4.6"), ["rank-1", "rank-4"])
        self.assertEqual(tax.rank_lineage("1"), ["rank-1"])
        self.assertEqual(tax.rank_lineage("9999"), [])

        # with ranks or  root_node
        self.assertEqual(tax.rank_lineage("5.2", ranks=["rank-1", "rank-3"]),
                         ["rank-1", "rank-3"])
        self.assertEqual(tax.rank_lineage("5.2", ranks=["rank-1", "XXX", "rank-3"]),
                         ["rank-1", tax.undefined_rank, "rank-3"])
        self.assertEqual(tax.rank_lineage("ZZZ", ranks=["rank-1", "XXX", "rank-3"]),
                         [])
        self.assertEqual(tax.rank_lineage("5.2", root_node="2.2"),
                         ["rank-2", "rank-3", "rank-4", "rank-5"])
        self.assertEqual(tax.rank_lineage("5.2", root_node="2.1"),
                         [])
        self.assertEqual(tax.rank_lineage("XXX", root_node="YYY"),
                         [])

        # with both
        self.assertEqual(tax.rank_lineage("5.2", root_node="2.2", ranks=["rank-3", "rank-4"]),
                         ["rank-3", "rank-4"])
        self.assertEqual(tax.rank_lineage("4.1", root_node="2.1", ranks=["rank-1", "rank-2", "rank-3", "rank-5"]),
                         [tax.undefined_rank, "rank-2", "rank-3", tax.undefined_rank])
        self.assertEqual(tax.rank_lineage("4.1", root_node="2.1", ranks=["rank-1", "rank-5"]),
                         [tax.undefined_rank, tax.undefined_rank])
        self.assertEqual(tax.rank_lineage("4.1", root_node="5.1", ranks=["rank-1", "rank-2", "rank-3", "rank-5"]),
                         [])
        self.assertEqual(tax.rank_lineage("XXXX", root_node="ZZZ", ranks=["CCC", "VVV"]),
                         [])

    def test_name_lineage(self):
        """
        test rank_lineage function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.name_lineage("5.2"), ["Node1", "Node2.2", "Node3.4", "Node4.4", "Node5.2"])
        self.assertEqual(tax.name_lineage("4.6"), ["Node1", "Node4.6"])
        self.assertEqual(tax.name_lineage("1"), ["Node1"])
        self.assertEqual(tax.name_lineage("9999"), [])

        # with ranks or  root_node
        self.assertEqual(tax.name_lineage("5.2", ranks=["rank-1", "rank-3"]),
                         ["Node1", "Node3.4"])
        self.assertEqual(tax.name_lineage("5.2", ranks=["rank-1", "XXX", "rank-3"]),
                         ["Node1", tax.undefined_name, "Node3.4"])
        self.assertEqual(tax.name_lineage("ZZZ", ranks=["rank-1", "XXX", "rank-3"]),
                         [])
        self.assertEqual(tax.name_lineage("5.2", root_node="2.2"),
                         ["Node2.2", "Node3.4", "Node4.4", "Node5.2"])
        self.assertEqual(tax.name_lineage("5.2", root_node="2.1"),
                         [])
        self.assertEqual(tax.name_lineage("XXX", root_node="YYY"),
                         [])

        # with both
        self.assertEqual(tax.name_lineage("5.2", root_node="2.2", ranks=["rank-3", "rank-4"]),
                         ["Node3.4", "Node4.4"])
        self.assertEqual(tax.name_lineage("4.1", root_node="2.1", ranks=["rank-1", "rank-2", "rank-3", "rank-5"]),
                         [tax.undefined_name, "Node2.1", "Node3.1", tax.undefined_name])
        self.assertEqual(tax.name_lineage("4.1", root_node="2.1", ranks=["rank-1", "rank-5"]),
                         [tax.undefined_name, tax.undefined_name])
        self.assertEqual(tax.name_lineage("4.1", root_node="5.1", ranks=["rank-1", "rank-2", "rank-3", "rank-5"]),
                         [])
        self.assertEqual(tax.name_lineage("XXXX", root_node="ZZZ", ranks=["CCC", "VVV"]),
                         [])

    def test_parent_rank(self):
        """
        test parent_rank function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.parent_rank("5.2", "rank-3"), "3.4")
        self.assertEqual(tax.parent_rank("4.1", "rank-2"), "2.1")
        self.assertEqual(tax.parent_rank("3.2", "rank-1"), "1")
        self.assertEqual(tax.parent_rank("3.2", "rank-4"), tax.undefined_node)
        self.assertEqual(tax.parent_rank("2.2", "XXXX"), tax.undefined_node)
        self.assertEqual(tax.parent_rank("CCCC", "XXXX"), tax.undefined_node)

    def test_stats(self):
        """
        test stats function
        """
        tax = CustomTx(files=self.test_file)
        stats = tax.stats()
        self.assertEqual(stats["nodes"], 14)
        self.assertEqual(stats["names"], 14)
        self.assertEqual(stats["ranks"], 14)
        self.assertEqual(stats["leaves"], 7)
        self.assertEqual(len(stats["ranked_nodes"]), 5)
        self.assertEqual(sum(stats["ranked_nodes"].values()), stats["nodes"])
        self.assertEqual(sum(stats["ranked_leaves"].values()), stats["leaves"])
        self.assertEqual(list(stats["ranked_leaves"].keys()), ["rank-4", "rank-5"])


    def test_build_lineages(self):
        """
        test build_lineages function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(len(tax._lineages), 0)
        tax.build_lineages()
        self.assertEqual(len(tax._lineages), 14)
        self.assertEqual(tax.lineage("5.2"), ["1", "2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("XXX"), [])

    def test_clear_lineages(self):
        """
        test clear_lineages function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(len(tax._lineages), 0)
        tax.build_lineages()
        self.assertEqual(len(tax._lineages), 14)
        tax.clear_lineages()
        self.assertEqual(len(tax._lineages), 0)
        self.assertEqual(tax.lineage("5.2"), ["1", "2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("XXX"), [])

    def test_check_consistency(self):
        """
        test check_consistency function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.check_consistency(), None)
        # delete node
        del tax._nodes["3.4"]
        self.assertRaises(AssertionError, tax.check_consistency)

        tax = CustomTx(files=self.test_file)
        # delete leaf node
        del tax._nodes["5.2"]
        self.assertEqual(tax.check_consistency(), None)

        tax = CustomTx(files=self.test_file)
        # delete root
        del tax._nodes["1"]
        # should raise error
        self.assertRaises(AssertionError, tax.check_consistency)

    def test_filter(self):
        """
        test filter function
        """
        # Ancestors
        tax = CustomTx(files=self.test_file)
        tax.filter("4.5")
        self.assertEqual(tax.stats()["nodes"], 3)
        self.assertEqual(tax.lineage("4.5"), ["1", "2.2", "4.5"])
        self.assertEqual(tax.leaves("1"), ["4.5"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["4.5", "XXXX"])
        self.assertEqual(tax.stats()["nodes"], 3)
        self.assertEqual(tax.lineage("4.5"), ["1", "2.2", "4.5"])
        self.assertCountEqual(tax.leaves("1"), ["4.5"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["4.1", "5.1", "5.2"])
        self.assertEqual(tax.stats()["nodes"], 9)
        self.assertEqual(tax.lineage("4.1"), ["1", "2.1", "3.1", "4.1"])
        self.assertCountEqual(tax.leaves("1"), ["4.1", "5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        tax.filter("1")
        self.assertEqual(tax.stats()["nodes"], 1)
        self.assertEqual(tax.lineage("1"), ["1"])
        self.assertCountEqual(tax.leaves("1"), ["1"])

        tax = CustomTx(files=self.test_file)
        tax.filter("XXXX")
        self.assertEqual(tax.stats()["nodes"], 1)

        # Descendants
        tax = CustomTx(files=self.test_file)
        tax.filter("3.4", desc=True)
        self.assertEqual(tax.stats()["nodes"], 5)
        self.assertEqual(tax.lineage("3.4"), ["1", "3.4"])
        self.assertCountEqual(tax.leaves("1"), ["5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["XXXXX", "3.4"], desc=True)
        self.assertEqual(tax.stats()["nodes"], 5)
        self.assertEqual(tax.lineage("3.4"), ["1", "3.4"])
        self.assertCountEqual(tax.leaves("1"), ["5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["3.2", "4.4"], desc=True)
        self.assertEqual(tax.stats()["nodes"], 7)
        self.assertEqual(tax.lineage("5.2"), ["1", "4.4", "5.2"])
        self.assertEqual(tax.lineage("4.5"), [])
        self.assertCountEqual(tax.leaves("1"), ["4.2", "4.3", "5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.stats()["nodes"], 14)
        tax.filter("1", desc=True)
        self.assertEqual(tax.stats()["nodes"], 14)
        
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.stats()["nodes"], 14)
        tax.filter("XXXXX", desc=True)
        self.assertEqual(tax.stats()["nodes"], 1)

    def test_write(self):
        """
        test write function
        """
        tax = CustomTx(files=self.test_file)
        outfile = self.tmp_dir + "default.tsv"
        tax.write(outfile)
        self.assertEqual(check_file(outfile), None)

        tax = CustomTx(files=self.test_file)
        outfile = self.tmp_dir + "all_cols.tsv"
        tax.write(outfile,
                  cols=["node", "latest", "parent", "rank", "name", "leaves", "children", "lineage", "rank_lineage", "name_lineage"])
        self.assertEqual(check_file(outfile), None)

        tax = CustomTx(files=self.test_file)
        outfile = self.tmp_dir + "sep_comma.tsv"
        tax.write(outfile,
                  sep=",")
        self.assertEqual(check_file(outfile), None)

        tax = CustomTx(files=self.test_file)
        outfile = self.tmp_dir + "sep_multi_underline.tsv"
        tax.write(outfile,
                  cols=["node", "lineage", "children", "leaves"],
                  sep_multi="_")
        self.assertEqual(check_file(outfile), None)

    def test_forwards(self):
        pass #ott
    def test_merged(self):
        pass #ncbi
    def test_constructor(self):
        pass #multitax, customtx
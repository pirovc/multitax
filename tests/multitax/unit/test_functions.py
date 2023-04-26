from multitax.utils import check_file
from multitax import *
from tests.multitax.utils import setup_dir
import unittest


class TestFunctions(unittest.TestCase):
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

        # Exact matches
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.search_name("Node1"), ["1"])
        self.assertCountEqual(tax.search_name("Node2.1"), ["2.1"])
        self.assertCountEqual(tax.search_name("Node5.2"), ["5.2"])
        self.assertCountEqual(tax.search_name("Node2."), [])

        # not exact matches
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.search_name(
            "Node2", exact=False), ["2.1", "2.2"])
        self.assertCountEqual(tax.search_name("Node2", exact=True), [])
        self.assertCountEqual(tax.search_name("Node1", exact=False), ["1"])
        self.assertCountEqual(tax.search_name("NotThere", exact=False), [])

        # Changing root name
        tax = CustomTx(files=self.test_file, root_name="AnotherRootName")
        self.assertCountEqual(tax.search_name("Node1", exact=False), [])
        self.assertCountEqual(tax.search_name(
            "AnotherRootName", exact=True), ["1"])
        self.assertCountEqual(tax.search_name("Another", exact=False), ["1"])

        # With specific rank
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.search_name(
            "Node2.1", exact=True, rank="rank-2"), ["2.1"])
        self.assertCountEqual(tax.search_name(
            "Node4.4", exact=True, rank="rank-4"), ["4.4"])
        self.assertCountEqual(tax.search_name(
            "Node", exact=False, rank="rank-5"), ["5.1", "5.2"])
        self.assertCountEqual(tax.search_name(
            "Node2.1", exact=True, rank="rank-3"), [])
        self.assertCountEqual(tax.search_name(
            "Node4.4", exact=True, rank="rank-1"), [])
        self.assertCountEqual(tax.search_name(
            "Node5", exact=False, rank="rank-XXX"), [])

    def test_nodes_rank(self):
        """
        test nodes_rank function
        """
        tax = CustomTx(files=self.test_file)
        self.assertCountEqual(tax.nodes_rank("rank-1"), ["1"])
        self.assertCountEqual(tax.nodes_rank("rank-4"),
                              ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"])
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
        self.assertCountEqual(
            tax.leaves(), ["4.1", "4.2", "4.3", "4.5", "4.6", "5.1", "5.2"])
        self.assertCountEqual(tax.leaves(
            "1"), ["4.1", "4.2", "4.3", "5.1", "5.2", "4.5", "4.6"])
        self.assertCountEqual(tax.leaves("2.2"), ["5.1", "5.2", "4.5"])
        self.assertCountEqual(tax.leaves("4.4"), ["5.1", "5.2"])
        self.assertCountEqual(tax.leaves("5.1"), ["5.1"])
        self.assertCountEqual(tax.leaves("999.999"), [])

    def test_lineage(self):
        """
        test lineage function
        """
        tax = CustomTx(files=self.test_file)
        # Use only assertEqual instead of assertCountEqual -> order matters
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
        self.assertEqual(tax.rank_lineage("5.2"), [
                         "rank-1", "rank-2", "rank-3", "rank-4", "rank-5"])
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
        self.assertEqual(tax.name_lineage("5.2"), [
                         "Node1", "Node2.2", "Node3.4", "Node4.4", "Node5.2"])
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

    def test_closest_parent(self):
        """
        test closest_parent function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.closest_parent(
            "5.2", ["rank-1", "rank-3"]), "3.4")
        self.assertEqual(tax.closest_parent(
            "5.2", ["rank-1", "rank-3", "rank-4"]), "4.4")
        self.assertEqual(tax.closest_parent(
            "5.2", ["rank-1", "rank-3", "rank-4", "rank-5"]), "5.2")
        self.assertEqual(tax.closest_parent(
            "5.2", ["rank-1", "rank-3", "rank-4", "rank-5", "XXXXX"]), "5.2")
        self.assertEqual(tax.closest_parent(
            "3.4", ["rank-1", "rank-4", "rank-5"]), "1")
        self.assertEqual(tax.closest_parent(
            "4.6", ["rank-1", "rank-2", "rank-3", "rank-5"]), "1")
        self.assertEqual(tax.closest_parent(
            "4.6", ["rank-2", "rank-3", "rank-5"]), tax.undefined_node)
        self.assertEqual(tax.closest_parent(
            "3.4", ["X", "Y", "Z"]), tax.undefined_node)
        self.assertEqual(tax.closest_parent("3.4", []), "3.4")

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
        self.assertCountEqual(list(stats["ranked_leaves"].keys()), [
                              "rank-4", "rank-5"])

    def test_build_lineages(self):
        """
        test build_lineages function
        """
        # build full lineages
        tax = CustomTx(files=self.test_file)
        self.assertEqual(len(tax._lineages), 0)
        tax.build_lineages()
        self.assertEqual(len(tax._lineages), 14)
        self.assertEqual(tax.lineage("5.2"), ["1", "2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("XXX"), [])
        # do not use stored lineage with keyword arguments
        self.assertEqual(tax.lineage("5.2", root_node="2.2"),
                         ["2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage(
            "5.2", ranks=["rank-2", "rank-4"]), ["2.2", "4.4"])
        self.assertEqual(tax.lineage("5.2", root_node="2.2", ranks=[
                         "rank-2", "rank-4"]), ["2.2", "4.4"])

        # build filtered lineages
        tax.clear_lineages()
        self.assertEqual(len(tax._lineages), 0)
        tax.build_lineages(root_node="2.2", ranks=["rank-2", "rank-4"])
        self.assertEqual(len(tax._lineages), 14)
        self.assertEqual(tax.lineage("5.2"), ["2.2", "4.4"])
        self.assertEqual(tax.lineage("XXX"), [])
        # do not use stored lineage with keyword arguments
        self.assertEqual(tax.lineage("5.2", root_node="3.4"),
                         ["3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("5.2", ranks=[]), [
                         "1", "2.2", "3.4", "4.4", "5.2"])
        self.assertEqual(tax.lineage("5.2", root_node="2.2", ranks=[
                         "rank-2", "rank-5"]), ["2.2", "5.2"])

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

    def test_translation(self):
        """
        test build_translation and tranlate functions (GTDB<->NCBI)
        """
        gtdb_tax = GtdbTx(files=["tests/multitax/data_minimal/gtdb_ar.tsv.gz",
                                 "tests/multitax/data_minimal/gtdb_bac.tsv.gz"])
        ncbi_tax = NcbiTx(files="tests/multitax/data_minimal/ncbi.tar.gz")

        # GTDB->NCBI
        # Should be no translation yet (g__Paenibacillus is contained in both test sets)
        self.assertCountEqual(gtdb_tax.translate("g__Paenibacillus"), [])
        gtdb_tax.build_translation(ncbi_tax, files=[
                                   "tests/multitax/data_minimal/gtdb_ar_metadata.tar.gz", "tests/multitax/data_minimal/gtdb_bac_metadata.tar.gz"])
        self.assertCountEqual(gtdb_tax.translate(
            "g__Paenibacillus"), ["44249"])

        # NCBI->GTDB
        # Should be no translation yet (g__Paenibacillus is contained in both test sets)
        self.assertCountEqual(ncbi_tax.translate("44249"), [])
        ncbi_tax.build_translation(gtdb_tax, files=[
                                   "tests/multitax/data_minimal/gtdb_ar_metadata.tar.gz", "tests/multitax/data_minimal/gtdb_bac_metadata.tar.gz"])
        self.assertCountEqual(ncbi_tax.translate(
            "44249"), ["g__Paenibacillus"])

        # Other translations not yet implemented
        ott_tax = OttTx(files="tests/multitax/data_minimal/ott.tgz")
        silva_tax = SilvaTx(files="tests/multitax/data_minimal/silva.txt.gz")
        gg_tax = GreengenesTx(files="tests/multitax/data_minimal/gg.txt.gz")
        with self.assertWarns(UserWarning):
            ncbi_tax.build_translation(ott_tax)
            ncbi_tax.build_translation(silva_tax)
            ncbi_tax.build_translation(gg_tax)
            gtdb_tax.build_translation(ott_tax)
            gtdb_tax.build_translation(silva_tax)
            gtdb_tax.build_translation(gg_tax)
            ott_tax.build_translation(silva_tax)
            ott_tax.build_translation(gg_tax)
            ott_tax.build_translation(gtdb_tax)
            ott_tax.build_translation(ncbi_tax)
            gg_tax.build_translation(ott_tax)
            gg_tax.build_translation(silva_tax)
            gg_tax.build_translation(gtdb_tax)
            gg_tax.build_translation(ncbi_tax)

    def test_check_consistency(self):
        """
        test check_consistency function
        """
        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.check_consistency(), None)
        # delete node
        del tax._nodes["3.4"]
        with self.assertRaises(ValueError):
            tax.check_consistency()

        tax = CustomTx(files=self.test_file)
        # delete leaf node
        del tax._nodes["5.2"]
        self.assertEqual(tax.check_consistency(), None)

        tax = CustomTx(files=self.test_file)
        # delete root
        del tax._nodes["1"]
        # should raise error
        with self.assertRaises(ValueError):
            tax.check_consistency()

    def test_filter(self):
        """
        test filter function
        """
        # Ancestors
        tax = CustomTx(files=self.test_file)
        tax.filter("4.5")
        self.assertEqual(tax.stats()["nodes"], 3)
        self.assertCountEqual(tax.lineage("4.5"), ["1", "2.2", "4.5"])
        self.assertCountEqual(tax.leaves("1"), ["4.5"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["4.5", "XXXX"])
        self.assertEqual(tax.stats()["nodes"], 3)
        self.assertCountEqual(tax.lineage("4.5"), ["1", "2.2", "4.5"])
        self.assertCountEqual(tax.leaves("1"), ["4.5"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["4.1", "5.1", "5.2"])
        self.assertEqual(tax.stats()["nodes"], 9)
        self.assertCountEqual(tax.lineage("4.1"), ["1", "2.1", "3.1", "4.1"])
        self.assertCountEqual(tax.leaves("1"), ["4.1", "5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        tax.filter("XXXX")
        self.assertEqual(tax.stats()["nodes"], 1)

        # Descendants
        tax = CustomTx(files=self.test_file)
        tax.filter("3.4", desc=True)
        self.assertEqual(tax.stats()["nodes"], 5)
        self.assertCountEqual(tax.lineage("3.4"), ["1", "3.4"])
        self.assertCountEqual(tax.leaves("1"), ["5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["XXXXX", "3.4"], desc=True)
        self.assertEqual(tax.stats()["nodes"], 5)
        self.assertCountEqual(tax.lineage("3.4"), ["1", "3.4"])
        self.assertCountEqual(tax.leaves("1"), ["5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        tax.filter(["3.2", "4.4"], desc=True)
        self.assertEqual(tax.stats()["nodes"], 7)
        self.assertCountEqual(tax.lineage("5.2"), ["1", "4.4", "5.2"])
        self.assertCountEqual(tax.lineage("4.5"), [])
        self.assertCountEqual(tax.leaves("1"), ["4.2", "4.3", "5.1", "5.2"])

        tax = CustomTx(files=self.test_file)
        self.assertEqual(tax.stats()["nodes"], 14)
        tax.filter("XXXXX", desc=True)
        self.assertEqual(tax.stats()["nodes"], 1)

    def test_add(self):
        """
        test add function
        """
        tax = CustomTx(files=self.test_file)
        # Add leaf node 5.3 to parent 4.4
        tax.add("5.3", "4.4")
        self.assertEqual(tax.check_consistency(), None)
        self.assertEqual(tax.parent("5.3"), "4.4")
        self.assertEqual(tax.name("5.3"), tax.undefined_name)
        self.assertEqual(tax.rank("5.3"), tax.undefined_rank)

        # Add another leaf on the 5.3 with name and rank
        tax.add("6.1", "5.3", name="Node6.1", rank="rank-6")
        self.assertEqual(tax.check_consistency(), None)
        self.assertEqual(tax.parent("6.1"), "5.3")
        self.assertEqual(tax.name("6.1"), "Node6.1")
        self.assertEqual(tax.rank("6.1"), "rank-6")
        self.assertEqual(tax.lineage("6.1"), [
                         "1", "2.2", "3.4", "4.4", "5.3", "6.1"])

        # Add node without valid parent, raises ValueError
        with self.assertRaises(ValueError):
            tax.add("6.2", "XXX")

        # Add already existing node
        with self.assertRaises(ValueError):
            tax.add("5.1", "4.4")

    def test_remove(self):
        """
        test remove function
        """
        tax = CustomTx(files=self.test_file)
        tax.remove("5.2")
        self.assertEqual(tax.latest("5.2"), tax.undefined_node)
        self.assertEqual(tax.parent("5.2"), tax.undefined_node)
        self.assertEqual(tax.name("5.2"), tax.undefined_node)
        self.assertEqual(tax.rank("5.2"), tax.undefined_node)
        self.assertEqual(tax.lineage("5.2"), [])

        # Initialize aux structures and clear them after removing node
        tax = CustomTx(files=self.test_file, build_name_nodes=True,
                       build_node_children=True, build_rank_nodes=True)
        self.assertNotEqual(len(tax._name_nodes), 0)
        self.assertNotEqual(len(tax._node_children), 0)
        self.assertNotEqual(len(tax._rank_nodes), 0)
        tax.remove("5.2")
        self.assertEqual(len(tax._name_nodes), 0)
        self.assertEqual(len(tax._node_children), 0)
        self.assertEqual(len(tax._rank_nodes), 0)

        # with check_consistency
        tax.remove("5.1", check_consistency=True)

        # Removing node that breaks the tree (allowed)
        tax.remove("3.1")
        # node is removed anyway
        self.assertEqual(tax.latest("3.1"), tax.undefined_node)
        with self.assertRaises(ValueError):
            tax.check_consistency()

        # Removing and raising execption
        with self.assertRaises(ValueError):
            tax.remove("3.2", check_consistency=True)
        # node is removed anyway
        self.assertEqual(tax.latest("3.2"), tax.undefined_node)

        # Removing root
        tax.remove("1")
        with self.assertRaises(ValueError):
            tax.check_consistency()

        # Removing node not present
        with self.assertRaises(ValueError):
            tax.remove("XXX")

    def test_prune(self):
        """
        test prune function
        """
        tax = CustomTx(files=self.test_file)

        self.assertCountEqual(tax.leaves("4.4"), ["5.1", "5.2"])
        tax.prune("4.4")
        self.assertEqual(tax.check_consistency(), None)
        self.assertCountEqual(tax.leaves("4.4"), ["4.4"])

        # Prune leaf node (nothing changes)
        self.assertCountEqual(tax.leaves("4.6"), ["4.6"])
        tax.prune("4.6")
        self.assertEqual(tax.check_consistency(), None)
        self.assertCountEqual(tax.leaves("4.6"), ["4.6"])

        # Prune multiple overlapping nodes
        self.assertCountEqual(tax.leaves("2.1"), ["4.1", "4.2", "4.3"])
        self.assertCountEqual(tax.leaves("3.2"), ["4.2", "4.3"])
        tax.prune(["2.1", "3.2"])
        self.assertEqual(tax.check_consistency(), None)
        self.assertCountEqual(tax.leaves("2.1"), ["2.1"])
        self.assertCountEqual(tax.leaves("3.2"), [])

        # Restar tax
        tax = CustomTx(files=self.test_file)
        # Prune multiple overlapping nodes (reversed)
        self.assertCountEqual(tax.leaves("2.1"), ["4.1", "4.2", "4.3"])
        self.assertCountEqual(tax.leaves("3.2"), ["4.2", "4.3"])
        tax.prune(["3.2", "2.1"])
        self.assertEqual(tax.check_consistency(), None)
        self.assertCountEqual(tax.leaves("2.1"), ["2.1"])
        self.assertCountEqual(tax.leaves("3.2"), [])

        # Pruning node not present
        with self.assertRaises(ValueError):
            tax.prune("XXX")

        # Prunning root node
        tax.prune(tax.root_node)
        self.assertEqual(len(tax._nodes), 1)

    def test_write(self):
        """
        test write function
        """
        tax = CustomTx(files=self.test_file)
        outfile = self.tmp_dir + "default.tsv"
        tax.write(outfile)
        self.assertEqual(check_file(outfile), None)

        tax = CustomTx(files=self.test_file)
        outfile = self.tmp_dir + "ranks.tsv"
        tax.write(outfile,
                  ranks=["rank-2", "rank-4"],
                  cols=["node", "rank", "lineage", "rank_lineage", "name_lineage"])
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

    def test_ott_forwards(self):
        """
        Test forwards functionality (ott only)
        """
        # forwards.tsv
        # id    replacement
        # 5044012 4603004
        # 391495  391494

        tax = OttTx(files="tests/multitax/data_minimal/ott.tgz")
        self.assertEqual(len(tax._forwards), 2)

        self.assertEqual(tax.parent("5044012"), tax.undefined_node)
        self.assertEqual(tax.latest("5044012"), "4603004")
        self.assertNotEqual(tax.parent(
            tax.latest("5044012")), tax.undefined_node)

        self.assertEqual(tax.parent("391495"), tax.undefined_node)
        self.assertEqual(tax.latest("391495"), "391494")
        self.assertNotEqual(tax.parent(
            tax.latest("391495")), tax.undefined_node)

    def test_ncbi_merged(self):
        """
        Test merged functionality (ncbi only)
        """
        # merged.dmp
        # 1235230 |   459525  |
        # 1235908 |   363999  |

        tax = NcbiTx(files="tests/multitax/data_minimal/ncbi.tar.gz")
        self.assertEqual(len(tax._merged), 2)

        self.assertEqual(tax.parent("1235230"), tax.undefined_node)
        self.assertEqual(tax.latest("1235230"), "459525")
        self.assertNotEqual(tax.parent(
            tax.latest("1235230")), tax.undefined_node)

        self.assertEqual(tax.parent("1235908"), tax.undefined_node)
        self.assertEqual(tax.latest("1235908"), "363999")
        self.assertNotEqual(tax.parent(
            tax.latest("1235908")), tax.undefined_node)

    def test_ncbi_extended_names(self):
        """
        Test extended names functionality (ncbi)
        """
        # on names.dmp
        # 363999  |   Xylariaceae sp. 5129    |       |   includes    |
        # 363999  |   Xylariaceae sp. 5151    |       |   includes    |
        # 363999  |   Xylariaceae sp. 5228    |       |   includes    |
        # 37990   |   mitosporic Xylariaceae  |       |   includes    |
        # 37990   |   Xylariaceae |       |   scientific name |

        tax = NcbiTx(files="tests/multitax/data_minimal/ncbi.tar.gz",
                     extended_names=False)
        tax_ex = NcbiTx(
            files="tests/multitax/data_minimal/ncbi.tar.gz", extended_names=True)

        # Exact match on scientific name
        self.assertCountEqual(tax.search_name("Xylariaceae"), ["37990"])
        self.assertCountEqual(tax_ex.search_name("Xylariaceae"), ["37990"])
        # All scientific names
        self.assertCountEqual(tax.search_name(
            "Xylariaceae", exact=False), ["37990"])
        self.assertCountEqual(tax_ex.search_name(
            "Xylariaceae", exact=False), ["37990"])
        # Exact match on scientific name forcing extended
        self.assertCountEqual(tax.search_name("Xylariaceae"), ["37990"])
        self.assertCountEqual(tax_ex.search_name(
            "Xylariaceae", force_extended=True), ["37990"])
        # All names
        self.assertCountEqual(tax.search_name(
            "Xylariaceae", exact=False), ["37990"])
        self.assertCountEqual(tax_ex.search_name(
            "Xylariaceae", exact=False, force_extended=True), ["37990", "363999"])
        # Exact name available only on extended
        self.assertCountEqual(tax.search_name(
            "mitosporic Xylariaceae", exact=True), [])
        self.assertCountEqual(tax_ex.search_name(
            "mitosporic Xylariaceae", exact=True), ["37990"])
        # Partial name available only on extended
        self.assertCountEqual(tax.search_name(
            "Xylariaceae sp.", exact=False), [])
        self.assertCountEqual(tax_ex.search_name(
            "Xylariaceae sp.", exact=False), ["363999"])

    def test_ott_extended_names(self):
        """
        Test extended names functionality (ott)
        """
        # on taxonomy.tsv
        # 4622    |   470454  |   Haemophilus sp. CCUG 32367  |   species |   silva:EU909664,ncbi:554010  |       |   sibling_higher  |
        # 4621    |   470454  |   Haemophilus sp. CCUG 35214  |   species |   silva:EU909665,ncbi:554011  |       |   sibling_higher  |
        # 158636  |   470454  |   Haemophilus sp. CCUG 30218  |   species |   silva:EU909662,ncbi:554007  |       |   sibling_higher  |
        # 391494  |   470454  |   Haemophilus sp. CCUG 31732  |   species |   silva:EU909663,ncbi:554009  |       |   sibling_higher  |
        # 525972  |   470454  |   Haemophilus pittmaniae HK 85    |   no rank - terminal  |   silva:AFUV01000004,ncbi:1035188 |
        # 788108  |   470454  |   Haemophilus sputorum    |   species |   silva:JF506644,ncbi:1078480,gbif:7522132    |
        # 470454  |   1098176 |   Haemophilus |   genus   |   silva:A16379/#6,ncbi:724,worms:571392,gbif:3219815,irmng:1307220    |       |       |
        # on synonyms.tsv
        # Hemophilus  |   470454  |   synonym |   Hemophilus (synonym for Haemophilus)    |   gbif:3219815,irmng:1307220  |
        # Haemophilus sp. HK 85   |   525972  |   equivalent name |   Haemophilus sp. HK 85 (synonym for Haemophilus pittmaniae HK 85)    |   ncbi:1035188    |
        # Haemophilus sp. CCUG 26672  |   788108  |   includes    |   Haemophilus sp. CCUG 26672 (synonym for Haemophilus sputorum)   |   ncbi:1078480    |
        # Haemophilus sp. CCUG 47809  |   788108  |   includes    |   Haemophilus sp. CCUG 47809 (synonym for Haemophilus sputorum)   |   ncbi:1078480    |

        tax = OttTx(files="tests/multitax/data_minimal/ott.tgz",
                    extended_names=False)
        tax_ex = OttTx(
            files="tests/multitax/data_minimal/ott.tgz", extended_names=True)

        # Exact match on scientific name
        self.assertCountEqual(tax.search_name("Haemophilus"), ["470454"])
        self.assertCountEqual(tax_ex.search_name("Haemophilus"), ["470454"])
        # All scientific names
        self.assertCountEqual(tax.search_name("Haemophilus sp.", exact=False), [
                              "391494", "158636", "4621", "4622"])
        self.assertCountEqual(tax_ex.search_name("Haemophilus sp.", exact=False), [
                              "391494", "158636", "4621", "4622"])
        # Exact match on scientific name forcing extended
        self.assertCountEqual(tax.search_name("Haemophilus"), ["470454"])
        self.assertCountEqual(tax_ex.search_name(
            "Haemophilus", force_extended=True), ["470454"])
        # All names
        self.assertCountEqual(tax.search_name("Haemophilus sp. CCUG", exact=False), [
                              "391494", "158636", "4621", "4622"])
        self.assertCountEqual(tax_ex.search_name("Haemophilus sp. CCUG", exact=False, force_extended=True), [
                              "391494", "158636", "4621", "4622", "788108"])
        # Exact name available only on extended
        self.assertCountEqual(tax.search_name(
            "Haemophilus sp. HK 85", exact=True), [])
        self.assertCountEqual(tax_ex.search_name(
            "Haemophilus sp. HK 85", exact=True), ["525972"])
        # Partial name available only on extended
        self.assertCountEqual(tax.search_name("CCUG 26672", exact=False), [])
        self.assertCountEqual(tax_ex.search_name(
            "CCUG 26672", exact=False), ["788108"])

from multitax import GreengenesTx, GtdbTx, NcbiTx, OttTx, SilvaTx, CustomTx
from tests.multitax.utils import setup_dir, uncompress_gzip, uncompress_tar_gzip
import unittest
import os
import sys
import random

sys.path.append("tests/multitax/")


class TestCommon(unittest.TestCase):

    tmp_dir = "tests/multitax/integration/tmp_common/"
    data_dir = "tests/multitax/data_minimal/"
    #data_dir = "tests/multitax/data_complete/"

    taxonomies = {}
    taxonomies["gtdb"] = {"class": GtdbTx,
                          "params": {"files": [data_dir + "gtdb_ar.tsv.gz",
                                               data_dir + "gtdb_bac.tsv.gz"]}}
    taxonomies["ncbi"] = {"class": NcbiTx,
                          "params": {"files": [data_dir + "ncbi.tar.gz"]}}
    taxonomies["silva"] = {"class": SilvaTx,
                           "params": {"files": [data_dir + "silva.txt.gz"]}}
    taxonomies["ott"] = {"class": OttTx,
                         "params": {"files": [data_dir + "ott.tgz"]}}
    taxonomies["greengenes"] = {"class": GreengenesTx,
                                "params": {"files": [data_dir + "gg.txt.gz"]}}
    taxonomies["custom"] = {"class": CustomTx,
                            "params": {"files": [data_dir + "custom.tsv.gz"]}}

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_basic(self):
        """
        Basic test with files
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            self.assertGreater(tax.stats()["nodes"], 0, t + " failed")

    def test_urls(self):
        """
        Using urls instead of files
        """
        for t in self.taxonomies:
            # simulate url with "file://" and absolute path
            urls = ["file://" + os.path.abspath(file)
                    for file in self.taxonomies[t]["params"]["files"]]
            tax = self.taxonomies[t]["class"](urls=urls)
            self.assertGreater(
                tax.stats()["nodes"], 0, t + " failed with urls")

    def test_urls_output_prefix(self):
        """
        Using urls and saving files on disk
        """
        for t in self.taxonomies:
            # simulate url with "file://" and absolute path
            urls = ["file://" + os.path.abspath(file)
                    for file in self.taxonomies[t]["params"]["files"]]
            tax = self.taxonomies[t]["class"](
                urls=urls, output_prefix=self.tmp_dir)
            self.assertGreater(
                tax.stats()["nodes"], 0, t + " failed with urls and output_prefix")

    def test_gzip_uncompressed(self):
        """
        Using uncompressed gzip files ("gtdb", "silva", "greengenes", "custom")
        """
        for t in self.taxonomies:
            if t in ["gtdb", "silva", "greengenes", "custom"]:
                uncompressed = []
                for file in self.taxonomies[t]["params"]["files"]:
                    if file.endswith(".gz"):
                        outfile = self.tmp_dir + os.path.basename(file)[:-3]
                        uncompress_gzip(file, outfile)
                        uncompressed.append(outfile)

                if uncompressed:
                    # Check if results are equal with compressed and uncompressed files
                    tax_compressed = self.taxonomies[t]["class"](
                        **self.taxonomies[t]["params"])
                    tax_uncompressed = self.taxonomies[t]["class"](
                        files=uncompressed)
                    self.assertEqual(tax_compressed.stats(), tax_uncompressed.stats(
                    ), t + " failed with uncompressed files")

    def test_tar_gzip_uncompressed_ncbi(self):
        """
        Using uncompressed tar gzip files for ncbi
        """

        # Ncbi
        tax_compressed = self.taxonomies["ncbi"]["class"](
            **self.taxonomies["ncbi"]["params"])
        uncompressed_files = uncompress_tar_gzip(
            f=self.taxonomies["ncbi"]["params"]["files"][0], outd=self.tmp_dir)
        self.assertIn("nodes.dmp", uncompressed_files)
        self.assertIn("names.dmp", uncompressed_files)
        self.assertIn("merged.dmp", uncompressed_files)
        tax_uncompressed = self.taxonomies["ncbi"]["class"](files=[self.tmp_dir + "nodes.dmp",
                                                                   self.tmp_dir + "names.dmp",
                                                                   self.tmp_dir + "merged.dmp"])
        # Results of compressed and uncompressed should match
        self.assertEqual(tax_uncompressed.stats(), tax_compressed.stats())

        # Ncbi with extended names
        ext_ncbi_conf = self.taxonomies["ncbi"].copy()
        ext_ncbi_conf["params"]["extended_names"] = True
        tax_compressed = ext_ncbi_conf["class"](**ext_ncbi_conf["params"])
        uncompressed_files = uncompress_tar_gzip(
            f=ext_ncbi_conf["params"]["files"][0], outd=self.tmp_dir)
        self.assertIn("nodes.dmp", uncompressed_files)
        self.assertIn("names.dmp", uncompressed_files)
        self.assertIn("merged.dmp", uncompressed_files)
        tax_uncompressed = ext_ncbi_conf["class"](files=[self.tmp_dir + "nodes.dmp",
                                                         self.tmp_dir + "names.dmp",
                                                         self.tmp_dir + "merged.dmp"],
                                                  extended_names=True)
        # Results of compressed and uncompressed should match
        self.assertEqual(tax_uncompressed.stats(), tax_compressed.stats())

    def test_tar_gzip_uncompressed_ott(self):
        """
        Using uncompressed tar gzip files for ott
        """
        # Ott
        tax_compressed = self.taxonomies["ott"]["class"](
            **self.taxonomies["ott"]["params"])
        uncompressed_files = uncompress_tar_gzip(
            f=self.taxonomies["ott"]["params"]["files"][0], outd=self.tmp_dir)
        self.assertIn("taxonomy.tsv", uncompressed_files)
        self.assertIn("forwards.tsv", uncompressed_files)
        tax_uncompressed = self.taxonomies["ott"]["class"](files=[self.tmp_dir + "taxonomy.tsv",
                                                                  self.tmp_dir + "forwards.tsv"])
        # Results of compressed and uncompressed should match
        self.assertEqual(tax_uncompressed.stats(), tax_compressed.stats())

        # Ott with extended names (synonyms.tsv)
        ext_ott_conf = self.taxonomies["ott"].copy()
        ext_ott_conf["params"]["extended_names"] = True
        tax_compressed = ext_ott_conf["class"](**ext_ott_conf["params"])
        uncompressed_files = uncompress_tar_gzip(
            f=ext_ott_conf["params"]["files"][0], outd=self.tmp_dir)
        self.assertIn("taxonomy.tsv", uncompressed_files)
        self.assertIn("forwards.tsv", uncompressed_files)
        self.assertIn("synonyms.tsv", uncompressed_files)
        tax_uncompressed = ext_ott_conf["class"](files=[self.tmp_dir + "taxonomy.tsv",
                                                        self.tmp_dir + "forwards.tsv",
                                                        self.tmp_dir + "synonyms.tsv"],
                                                 extended_names=True)
        # Results of compressed and uncompressed should match
        self.assertEqual(tax_uncompressed.stats(), tax_compressed.stats())

    def test_inconsistent(self):
        """
        Test parsing inconsistent taxonomies
        """
        for t in self.taxonomies:
            # Delete root
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            tax._remove(tax.root_node)
            self.assertRaises(AssertionError, tax.check_consistency)

            # Delete random node (parent from random leaf)
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            tax._remove(tax.parent(random.choice(tax.leaves())))
            self.assertRaises(AssertionError, tax.check_consistency)

            # Delete random leaf (do not generate inconsistency)
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            tax._remove(random.choice(tax.leaves()))
            self.assertEqual(tax.check_consistency(), None)

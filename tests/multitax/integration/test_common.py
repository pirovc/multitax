import unittest
import os
import sys

sys.path.append("tests/multitax/")
from utils import setup_dir, uncompress_gzip

from multitax import GreengenesTx, GtdbTx, NcbiTx, OttTx, SilvaTx, CustomTx


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

    def test_consistency(self):
        """
        Check consistency of test files
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            self.assertFalse(tax.check_consistency(), t + " taxonomy is not consistent")

    def test_urls(self):
        """
        Using urls instead of files
        """
        for t in self.taxonomies:
            # simulate url with "file://" and absolute path
            urls = ["file://" + os.path.abspath(file) for file in self.taxonomies[t]["params"]["files"]]
            tax = self.taxonomies[t]["class"](urls=urls)
            self.assertGreater(tax.stats()["nodes"], 0, t + " failed with urls")

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
                    tax_compressed = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
                    tax_uncompressed = self.taxonomies[t]["class"](files=uncompressed)
                    self.assertEqual(tax_compressed.stats(), tax_uncompressed.stats(), t + " failed with uncompressed files")

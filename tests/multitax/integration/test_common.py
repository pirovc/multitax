import unittest
import os

from utils import setup_dir, uncompress_gzip

from multitax import GreengenesTx, GtdbTx, NcbiTx, OttTx, SilvaTx


class TestCommon(unittest.TestCase):

    base_dir = "tests/multitax/integration/"
    tmp_dir = base_dir + "tmp_common/"

    data_dir = base_dir + "data_minimal/"
    #data_dir = base_dir + "data_complete/"

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

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_basic(self):
        """
        Basic test with files
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            self.assertGreater(tax.stats()["nodes"], 0)

    def test_urls(self):
        """
        Using urls instead of files
        """
        for t in self.taxonomies:
            # simulate url with "file://" and absolute path
            urls = ["file://" + os.path.abspath(file) for file in self.taxonomies[t]["params"]["files"]]
            tax = self.taxonomies[t]["class"](urls=urls)
            self.assertGreater(tax.stats()["nodes"], 0)

    def test_gzip_uncompressed(self):
        """
        Using uncompressed gzip files ("gtdb", "silva", "greengenes")
        """
        for t in self.taxonomies:
            if t in ["gtdb", "silva", "greengenes"]:
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
                    self.assertEqual(tax_compressed.stats(), tax_uncompressed.stats())

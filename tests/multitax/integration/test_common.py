import unittest
import os

from multitax.gtdbtx import GtdbTx
from multitax.ncbitx import NcbiTx
from multitax.silvatx import SilvaTx
from multitax.otttx import OttTx
from multitax.greengenestx import GreengenesTx


class TestCommon(unittest.TestCase):

    data_dir = "tests/multitax/integration/data/"
    taxonomies = {}
    taxonomies["gtdb"] = {"class": GtdbTx,
                          "params": {"files": [data_dir + "gtdb_mini_ar.tsv.gz",
                                               data_dir + "gtdb_mini_bac.tsv.gz"]}}
    taxonomies["ncbi"] = {"class": NcbiTx,
                          "params": {"files": [data_dir + "ncbi_mini.tar.gz"]}}
    taxonomies["silva"] = {"class": SilvaTx,
                           "params": {"files": [data_dir + "silva_mini.txt.gz"]}}
    taxonomies["ott"] = {"class": OttTx,
                         "params": {"files": [data_dir + "ott_mini.tgz"]}}
    taxonomies["greengenes"] = {"class": GreengenesTx,
                                "params": {"files": [data_dir + "gg_mini.txt.gz"]}}

    def test_basic(self):
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            self.assertGreater(tax.stats()["nodes"], 0)

    def test_urls(self):
        for t in self.taxonomies:
            # simulate url with "file://" and absolute path
            urls = ["file://" + os.path.abspath(file) for file in self.taxonomies[t]["params"]["files"]]
            tax = self.taxonomies[t]["class"](urls=urls)
            self.assertGreater(tax.stats()["nodes"], 0)

import unittest
from multitax.gtdbtx import GtdbTx
from multitax.ncbitx import NcbiTx
from multitax.silvatx import SilvaTx
from multitax.otttx import OttTx
from multitax.greengenestx import GreengenesTx
from multitax.emptytx import EmptyTx


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

    def test_empty(self):
        tax = EmptyTx()
        stats = tax.stats()
        # Only root node
        self.assertEqual(stats["nodes"], 1)
        # No input sources
        self.assertFalse(tax.sources)

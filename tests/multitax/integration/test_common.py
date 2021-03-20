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
                          "params": {"files": [data_dir + "bac120_taxonomy.tsv.gz",
                                               data_dir + "ar122_taxonomy.tsv.gz"]}}
    taxonomies["ncbi"] = {"class": NcbiTx,
                          "params": {"files": [data_dir + "taxdump.tar.gz"]}}
    taxonomies["silva"] = {"class": SilvaTx,
                           "params": {"files": [data_dir + "tax_slv_ssu_138.1.txt.gz"]}}
    taxonomies["ott"] = {"class": OttTx,
                         "params": {"files": [data_dir + "ott3.2.tgz"]}}
    taxonomies["greengenes"] = {"class": GreengenesTx,
                                "params": {"files": [data_dir + "gg_13_5_taxonomy.txt.gz"]}}

    def test_basic(self):
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            stats = tax.stats()
            self.assertGreater(stats["nodes"], 0)
    
    def test_empty(self):
        tax = EmptyTx()
        stats = tax.stats()
        # Only root node
        self.assertEqual(stats["nodes"], 1)
        # No input sources
        self.assertFalse(stats.sources)

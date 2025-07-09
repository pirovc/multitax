from multitax import GreengenesTx, GtdbTx, NcbiTx, OttTx, SilvaTx, CustomTx
from tests.multitax.utils import setup_dir, uncompress_gzip, uncompress_tar_gzip
import unittest
import os
import sys
import random

sys.path.append("tests/multitax/")


@unittest.skip('Skip online by default')
class TestOnline(unittest.TestCase):

    tmp_dir = "tests/multitax/integration/tmp_online/"

    taxonomies = {}
    taxonomies["gtdb"] = {"class": GtdbTx}
    taxonomies["ncbi"] = {"class": NcbiTx}
    taxonomies["silva"] = {"class": SilvaTx}
    taxonomies["ott"] = {"class": OttTx}
    taxonomies["greengenes"] = {"class": GreengenesTx}
    # todo test online custom

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_online_default(self):
        """
        Default test online
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"]()
            self.assertGreater(tax.stats()["nodes"], 0, t + " failed")

    def test_online_output_prefix(self):
        """
        Saving files on disk
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](output_prefix=self.tmp_dir)
            self.assertGreater(
                tax.stats()["nodes"], 0, t + " failed with urls and output_prefix")

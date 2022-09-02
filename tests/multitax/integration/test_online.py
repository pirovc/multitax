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
    taxonomies["gtdb"] = {"class": GtdbTx, "params": {}}
    taxonomies["ncbi"] = {"class": NcbiTx, "params": {}}
    taxonomies["silva"] = {"class": SilvaTx, "params": {}}
    taxonomies["ott"] = {"class": OttTx, "params": {}}
    taxonomies["greengenes"] = {"class": GreengenesTx, "params": {}}
    # todo test online custom

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_online_deafult(self):
        """
        Default test online
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"])
            self.assertGreater(tax.stats()["nodes"], 0, t + " failed")

    def test_online_output_prefix(self):
        """
        Saving files on disk
        """
        for t in self.taxonomies:
            tax = self.taxonomies[t]["class"](**self.taxonomies[t]["params"], output_prefix=self.tmp_dir)
            self.assertGreater(
                tax.stats()["nodes"], 0, t + " failed with urls and output_prefix")

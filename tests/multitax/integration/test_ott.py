import unittest
import sys

sys.path.append("tests/multitax/")
from utils import setup_dir, uncompress_tar_gzip
from multitax import OttTx


class TestOtt(unittest.TestCase):

    tmp_dir = "tests/multitax/integration/tmp_ott/"
    data_dir = "tests/multitax/data_minimal/"
    #data_dir = "tests/multitax/data_complete/"
    default_params = {"files": data_dir + "ott.tgz"}

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_tar_gzip_uncompressed(self):
        """
        Using uncompressed tar gzip files
        """
        tax_compressed = OttTx(**self.default_params)

        uncompressed_files = uncompress_tar_gzip(self.default_params["files"], self.tmp_dir)
        self.assertIn("taxonomy.tsv", uncompressed_files)
        self.assertIn("forwards.tsv", uncompressed_files)
        tax_uncompressed = OttTx(files=[self.tmp_dir + "taxonomy.tsv",
                                        self.tmp_dir + "forwards.tsv"])

        # Results of compressed and uncompressed should match
        self.assertEqual(tax_uncompressed.stats(), tax_compressed.stats())

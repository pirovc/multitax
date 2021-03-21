import unittest

from utils import setup_dir, uncompress_tar_gzip
from multitax.ncbitx import NcbiTx


class TestNcbi(unittest.TestCase):
    base_dir = "tests/multitax/integration/"
    tmp_dir = base_dir + "tmp_ncbi/"

    data_dir = base_dir + "data_minimal/"
    #data_dir = base_dir + "data_complete/"

    default_params = {"files": data_dir + "ncbi.tar.gz"}

    @classmethod
    def setUpClass(self):
        setup_dir(self.tmp_dir)

    def test_tar_gzip_uncompressed(self):
        """
        Using uncompressed tar gzip files
        """
        tax_compressed = NcbiTx(**self.default_params)

        uncompressed_files = uncompress_tar_gzip(self.default_params["files"], self.tmp_dir)
        self.assertIn("nodes.dmp", uncompressed_files)
        self.assertIn("names.dmp", uncompressed_files)
        self.assertIn("merged.dmp", uncompressed_files)
        tax_uncompressed = NcbiTx(files=[self.tmp_dir + "nodes.dmp",
                                         self.tmp_dir + "names.dmp",
                                         self.tmp_dir + "merged.dmp"])

        # Results of compressed and uncompressed should match
        self.assertEqual(tax_uncompressed.stats(), tax_compressed.stats())

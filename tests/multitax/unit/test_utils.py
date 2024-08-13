import unittest
from multitax.utils import fuzzy_find_download_links


class TestUtils(unittest.TestCase):
    def test_fuzzy_find_download_links(self):
        registery_url = "https://www.arb-silva.de/no_cache/download/archive/current/Exports/taxonomy/"
        links = fuzzy_find_download_links(registery_url, ".*tax_slv_ssu_.*.txt.gz$")
        self.assertTrue('https://www.arb-silva.de/fileadmin/silva_databases/current/Exports/taxonomy/tax_slv_ssu_' in links[0])

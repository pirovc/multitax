import unittest
from multitax.utils import fuzzy_find_download_link


class TestUtils(unittest.TestCase):
    def fuzzy_find_download_link(self):
        links = fuzzy_find_download_link("https://www.arb-silva.de/fileadmin/silva_databases/current/Exports/taxonomy")
        print(links)
        pass

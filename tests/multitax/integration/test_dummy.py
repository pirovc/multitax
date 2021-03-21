import unittest

from multitax import DummyTx


class TestDummy(unittest.TestCase):

    def test_empty(self):
        tax = DummyTx()
        stats = tax.stats()
        # Only root node
        self.assertEqual(stats["nodes"], 1)
        # No input sources
        self.assertFalse(tax.sources)

import unittest
from multitax.multitax import MultiTax
from multitax import DummyTx


class TestDummy(unittest.TestCase):

    def test_multitax(self):
        tax = MultiTax()
        stats = tax.stats()
        # Only root node
        self.assertEqual(stats["nodes"], 1)
        # No input sources
        self.assertFalse(tax.sources)

    def test_dummy(self):
        tax = DummyTx()
        stats = tax.stats()
        # Only root node
        self.assertEqual(stats["nodes"], 1)
        # No input sources
        self.assertFalse(tax.sources)

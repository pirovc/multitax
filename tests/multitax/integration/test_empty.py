import unittest

from multitax.emptytx import EmptyTx


class TestEmpty(unittest.TestCase):

    def test_empty(self):
        tax = EmptyTx()
        stats = tax.stats()
        # Only root node
        self.assertEqual(stats["nodes"], 1)
        # No input sources
        self.assertFalse(tax.sources)

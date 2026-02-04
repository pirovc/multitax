from .multitax import MultiTax


class DummyTx(MultiTax):
    def __init__(self, **kwargs):
        """
        DummyTx() - Dummy empty taxonomy

        Parameters:

        * \*\*kwargs defined at `multitax.multitax.MultiTax`
        """
        super().__init__(**kwargs)

    def __repr__(self):
        stats = ["{}={}".format(k, repr(v)) for (k, v) in self.stats().items()]
        return "DummyTx({})".format(", ".join(stats))

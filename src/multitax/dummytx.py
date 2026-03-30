from multitax.utils import format_repr
from .multitax import MultiTax


class DummyTx(MultiTax):
    def __init__(self, **kwargs):
        """
        DummyTx() - Dummy empty taxonomy

        Parameters:

        * \\*\\*kwargs defined at `multitax.multitax.MultiTax`
        """
        super().__init__(**kwargs)

    def __repr__(self):
        return format_repr(inst=self)

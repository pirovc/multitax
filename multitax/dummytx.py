from .multitax import MultiTax


class DummyTx(MultiTax):

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'DummyTx({})'.format(', '.join(args))

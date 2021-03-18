from multitax.multitax import MultiTax


class EmptyTx(MultiTax):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'EmptyTx({})'.format(', '.join(args))

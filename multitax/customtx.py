from .multitax import MultiTax


class CustomTx(MultiTax):

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'CustomTx({})'.format(', '.join(args))

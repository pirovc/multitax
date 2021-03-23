from .multitax import MultiTax


class CustomTx(MultiTax):

    _urls = []
    _root_node = "1"

    def __init__(self, cols: list=None, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'CustomTx({})'.format(', '.join(args))

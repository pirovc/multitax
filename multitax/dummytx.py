from .multitax import MultiTax


class DummyTx(MultiTax):

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
  
    default_root_node = "111"
    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'DummyTx({})'.format(', '.join(args))
from .multitax import MultiTax


class CustomTx(MultiTax):
    
    def __init__(self, cols: list=None, **kwargs):
        """
        Constructor of the class CustomTx

        Parameters:
        * **cols** ***[list, dict]***: List of fields to be parsed or a dictionary
        * \*\*kwargs defined at `multitax.multitax.MultiTax`
        """
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'CustomTx({})'.format(', '.join(args))

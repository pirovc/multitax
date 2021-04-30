from .multitax import MultiTax


class CustomTx(MultiTax):

    _required_cols = ["node", "parent"]
    _possible_cols = ["node", "parent", "rank", "name"]

    def __init__(self, cols: list=["node", "parent", "rank", "name"], sep: str="\t", **kwargs):
        """
        CustomTx()

        Parameters:
        * **cols** *[list, dict]*: List of fields to be parsed or a dictionary with {field: column index}. Options: "node", "parent", "rank", "name"
        * **sep** *[str]*: Separator of fields
        * **\*\*kwargs** defined at `multitax.multitax.MultiTax`

        Example:

        tax_custom1 = CustomTx(files="my_custom_tax.tsv", cols=["node","parent","rank"])
        tax_custom2 = CustomTx(files="my_custom_tax.tsv", cols={"node": 0, "parent": 1, "name": 5, "rank": 3})
        """

        self._cols = self._parse_cols(cols)
        self._sep = sep
        super().__init__(**kwargs)

    def __repr__(self):
        args = ['{}={}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'CustomTx({})'.format(', '.join(args))

    def _parse(self, fhs, **kwargs):
        nodes = {}
        ranks = {}
        names = {}
        for source, fh in fhs.items():
            for line in fh:
                try:
                    fields = line.rstrip().split(self._sep)
                except:
                    fields = line.decode().rstrip().split(self._sep)

                node = fields[self._cols["node"]]
                nodes[node] = fields[self._cols["parent"]]
                if "name" in self._cols:
                    names[node] = fields[self._cols["name"]]
                if "rank" in self._cols:
                    ranks[node] = fields[self._cols["rank"]]
            return nodes, ranks, names

    def _parse_cols(self, cols):
        if isinstance(cols, list):
            cols = {c: i for i, c in enumerate(cols)}

        for rc in self._required_cols:
            if rc not in cols:
                raise ValueError(rc + " is a required column")

        for c in cols:
            if c not in self._possible_cols:
                raise ValueError(c + " is not a valid column: " + ",".join(self._possible_cols))

        return cols

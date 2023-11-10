"""" classes and functions

"""


class BrickModel():
    """

    """
    def __init__(self, _graph=None):
        self.g = _graph

    def get_entities(self, brick_class=None):
        res = self.g.query(
            f"""SELECT * WHERE {{
                ?sub a brick:{brick_class} 
                     }}"""
        )
        list_ = res.bindings
        list_friendly = [x.get('sub') for x in list_]

        return list_friendly
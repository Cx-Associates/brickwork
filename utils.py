"""" classes and functions

"""


class Entity():
    """

    """
    def __init__(self, uri_ref, g):
        self.uri_ref = uri_ref
        name = str(uri_ref).split('#')[1]
        self.name = name
        self.g = g

    def get_timeseries(self, relationship, inverse_relationship=None):
        """

        :return:
        """
        res = self.g.query(
            f"""SELECT ?predicate ?object WHERE {{
                <%s> ?predicate ?object . 
                     }}
            """ % self.uri_ref
        )
        list_ = res.bindings

        return list_ #ToDo: proof of concept is good ... maybe move this method to something else for the future and
        # then get back to fetching the timeseries

class BrickModel():
    """

    """
    def __init__(self, _graph=None):
        self.g = _graph
        self.time_frame = (None, None)

    def get_entities(self, brick_class=None):
        res = self.g.query(
            f"""SELECT * WHERE {{
                ?sub a brick:{brick_class} 
                     }}"""
        )
        list_ = res.bindings
        list_friendly = [Entity(x.get('sub'), self.g) for x in list_]

        return list_friendly
"""" classes and functions

"""

class RDF():
    """

    """
    def __init__(self, graph):
        self.g = graph

    def unpack(self, result):
        """

        :param result:
        :return:
        """
        list_ = result.bindings
        list_friendly = [Entity(x.get('sub'), self.g) for x in list_]
        return list_friendly


class Entity(RDF):
    """

    """
    def __init__(self, uri_ref, g):
        self.uri_ref = uri_ref
        name = str(uri_ref).split('#')[1]
        self.name = name
        self.g = g

    def get_all_relationships(self):
        """

        :return:
        """
        res = self.g.query(
            f"""SELECT ?predicate ?object WHERE {{
                <%s> ?predicate ?object . 
                     }}
            """ % self.uri_ref
        )
        return self.unpack(res)

    def get_timeseries(self, relationship, inverse_relationship=None):
        """

        :return:
        """
        res = self.g.query(
            f"""SELECT ?predicate ?object WHERE {{
                <%s> ?brick.{relationship} ?object .
                    }}
            """ % self.uri_ref
        )
        return self.unpack(res)


class BrickModel(RDF):
    """

    """
    def __init__(self, _graph=None):
        self.g = _graph
        self.time_frame = (None, None)

    def get_entities(self, brick_class=None):
        """

        :param brick_class:
        :return: a list of instances of the Entity class
        """
        res = self.g.query(
            f"""SELECT * WHERE {{
                ?sub a brick:{brick_class} 
                     }}"""
        )
        return self.unpack(res)

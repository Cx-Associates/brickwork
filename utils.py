"""" classes and functions

"""

class RDF():
    """

    """
    def __init__(self, graph):
        self.g = graph

    def unpack(self, result, element='subject'):
        """

        :param result:
        :return:
        """
        list_ = result.bindings
        list_friendly = [Entity(x.get(element), self.g) for x in list_]
        return list_friendly


class Entity(RDF):
    """

    """
    def __init__(self, uri_ref, g):
        self.uri_ref = uri_ref
        try:
            name = str(uri_ref).split('#')[1]
        except IndexError:
            name = uri_ref
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
        return res.bindings

    def get_timeseries(self, relationship, inverse_relationship=None):
        """

        :return:
        """
        res = self.g.query(
            f"""SELECT ?predicate ?object WHERE {{
                <%s> brick:{relationship} ?object .
                    }}
            """ % self.uri_ref
        )
        # now get the external timeseries reference of the result of the previous query
        entity = self.unpack(res, 'object')[0] #ToDo: not safe. prepare to deal with multiple results
        res2 = self.g.query(
            f"""SELECT ?id WHERE {{
                ?bnode ref:hasTimeseriesId ?id {{
                    SELECT ?bnode WHERE {{ <%s> ref:hasExternalReference ?bnode }}
                }}
            }}
        """ % entity.uri_ref
        )
        entity2 = self.unpack(res2, 'id')[0]

        return entity2



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
                ?subject a brick:{brick_class} 
                     }}"""
        )
        return self.unpack(res)

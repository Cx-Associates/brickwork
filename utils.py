"""" classes and functions

"""
# from api import get_timeseries
from .api import get_timeseries
from brickschema import Graph

class RdfParser():
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


class BrickModel(RdfParser):
    """

    """
    def __init__(self, filepath):
        self.time_frame = (None, None)
        self.g = Graph(load_brick=True)
        self.g.load_file(filepath)

    def set_time_frame(self, tuple):
        self.time_frame = tuple

    def get_entities(self, name=None, brick_class=None):
        """

        :param brick_class:
        :return: a list of instances of the Entity class
        """
        if brick_class is not None:
            res = self.g.query(
                f"""SELECT * WHERE {{
                    ?subject a brick:{brick_class} 
                         }}"""
            )
            list_ = self.unpack(res)
            for entity in list_:
                entity.model = self
        if name is not None:
            res = self.g.query(
                f"""SELECT ?subject WHERE {{
                    ?subject brick:name {name} 
                         }}"""
            )
            list_ = self.unpack(res)
            for entity in list_:
                entity.model = self

        return list_

class Entity(RdfParser):
    """

    """
    def __init__(self, uri_ref, g):
        self.uri_ref = uri_ref
        try:
            name = str(uri_ref).split('#')[1]
        except IndexError:
            name = str(uri_ref)
        self.name = name
        self.g = g
        self.model = None

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

    def get_timeseries_id(self, relationship, inverse_relationship=None):
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
        # todo: raise error if no result (to prevent extra API call)

        return entity2

    def get_timeseries(self, relationship): #change from relationship to brick:type of object
        """

        :param relationship:
        :return:
        """
        ts_id = self.get_timeseries_id(relationship)
        res = self.g.query(
            """SELECT ?str WHERE { bldg:database bldg:connstring ?str}"""
        )
        list_ = self.unpack(res, 'str')
        connstr = list_[0].name
        start, end = self.model.time_frame[0], self.model.time_frame[1]
        timestr = f'/timeseries?start_time={start}&end_time={end}'
        fullstr = connstr + ts_id.name + timestr
        df = get_timeseries(fullstr)

        return df


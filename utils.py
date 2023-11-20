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

    def unpack(self, result, elements=['name', 'brick_class']):
        """

        :param result:
        :return:
        """
        list_ = result.bindings
        list_friendly = [Entity(x.get(elements[0]), self.g) for x in list_]
        i = 0
        for x in list_:
            for element in elements[1:]:
                uri = x.get(element)
                try:
                    str_ = str(uri).split('#')[1]
                except IndexError:
                    str_ = str(uri)
                list_friendly[0].__setattr__(element, str_)
            i += 1
        return list_friendly


class BrickModel(RdfParser):
    """

    """
    def __init__(self, filepath):
        self.g = Graph(load_brick=True)
        self.g.load_file(filepath)

    def get_entities(self, name=None, brick_class=None):
        """Get a list of entities filtered by name, by class, or by both.

        :param brick_class:
        :return: a list of instances of the Entity class
        """
        predicate = '?brick_class'
        filter = ''
        if name is not None:
            filter = f'FILTER(?name = bldg:{name})' #ToDo:depends on prefix 'bldg'
        if brick_class is not None:
            predicate = f'brick:{brick_class}'
        if name is None and brick_class is None:
            raise('Need to pass either a brick_class, a name, or both into this function.')
        qry = f"""SELECT ?name ?brick_class WHERE {{
                    ?name rdf:type {predicate} . {filter}
                    }}"""
        res = self.g.query(qry)
        list_ = self.unpack(res, ['name', 'brick_class']) #ToDo: also need 'p' correct? under some conditions?
        for entity in list_:
            entity.model = self  #ToDo: check if we need this
            # entity.brick_class = self.get_entity_brick_class(entity.name)

        return list_

    def get_entities_of_system(self, system_name):
        """

        :param system_name:
        :return:
        """
        qry = f"""SELECT ?obj WHERE {{
            bldg:{system_name}  brick:hasPart|brick:hasInputSubstance|brick:hasOutputSubstance  ?obj
        }}"""
        res = self.g.query(qry)
        return self.unpack(res, 'obj')

    def get_entity_brick_class(self, name):
        """

        :param uri:
        :return:
        """
        qry = f"""SELECT ?obj WHERE {{
            bldg:{name}  a  ?obj
        }}"""
        res = self.g.query(qry)
        return self.unpack(res, 'obj')



    def get_system_timeseries(self, system_name, time_frame):
        """

        :param system_name:
        :param time_frame:
        :return:
        """
        entities_list = self.get_entities_of_system(system_name)
        series_dict = {}
        for entity in entities_list:
            ts_response = entity.get_all_timeseries('hasPoint', time_frame)
            # df2 = entity.get_timeseries('isMeteredBy', time_frame)  #ToDo:graph may use inverse, and reasoning isn't
            # working
            # quite yet



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
        self.g = g  #ToDo: need this?
        self.model = None
        self.brick_class = None

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

    def get_all_timeseries(self, time_frame, relationship='hasPoint'):
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
        start, end = time_frame[0], time_frame[1]
        timestr = f'/timeseries?start_time={start}&end_time={end}'
        fullstr = connstr + ts_id.name + timestr
        df = get_timeseries(fullstr)

        return df


class TimeseriesResponse():
    """

    """
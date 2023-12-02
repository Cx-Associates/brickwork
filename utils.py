"""" classes and functions

"""

import pandas as pd
import warnings
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
        if len(list_) == 0:
            if name is not None and brick_class is None:
                raise Exception(f'No entities found in graph named {name}. \n Query: {qry}')
            elif name is None and brick_class is not None:
                raise Exception(f'No entities in graph of brick class {brick_class}. \n Query: {qry}')
            elif name is not None and brick_class is not None:
                raise Exception(f'No entities in graph named {name} of class {brick_class}. \n Query: {qry}')
            else:
                raise Exception(f'No entities found with query {qry}.')
        for entity in list_:
            entity.model = self  #ToDo: check if we need this
            if brick_class is not None:
                entity.brick_class = brick_class

        entity_list = EntityList(list_)
        return entity_list

    def get_entities_of_system(self, system_name):
        """

        :param system_name:
        :return:
        """
        qry = f"""SELECT ?obj WHERE {{
            bldg:{system_name}  brick:hasPart|brick:hasInputSubstance|brick:hasOutputSubstance  ?obj
        }}"""
        res = self.g.query(qry)
        list_ = self.unpack(res, ['obj'])
        entity_list = EntityList(list_)

        return entity_list

    def get_entity_brick_class(self, name):
        """

        :param uri:
        :return:
        """
        qry = f"""SELECT ?obj WHERE {{
            bldg:{name}  a  ?obj
        }}"""
        res = self.g.query(qry)
        return self.unpack(res, ['obj'])



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
        self.last_response = {}

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

    def get_timeseries_ids(self, relationship='hasPoint', inverse_relationship=None):
        """

        :param relationship: hasPoint is default because of timeseries storage conventions defined by the BrickSchema
        documentation
        :return:
        """
        timeseries_ids = []
        res = self.g.query(
            f"""SELECT ?predicate ?object WHERE {{
                <%s> brick:{relationship} ?object .
                    }}
            """ % self.uri_ref
        )
        # now get the external timeseries reference of the result of the previous query
        points = self.unpack(res, ['object'])
        for point in points:
            res2 = self.g.query(
                f"""SELECT ?s ?id ?unit WHERE {{
                    ?bnode ref:hasTimeseriesId ?id {{
                        SELECT ?unit WHERE {{
                            bldg:{point.name} ref:hasExternalReference ?bnode .
                            bldg:{point.name} brick:hasUnit ?unit .
                            }}
                    }}
                }}
            """
            )
            ts_id = self.unpack(res2, ['id', 'unit'])
            if len(ts_id) == 0:
                msg = f"!! {self.name} point {point.name} doesn't have TimeseriesId associated with it in the graph."
                warnings.warn(msg, Warning)
                continue
            if len(ts_id) > 1:
                msg = f'!! {self.name} point {point.name} has more than one associated TimeseriesId. Returning only ' \
                      f'the first one. If this is not a mistake in the graph, then please refactor this function to  ' \
                      f'deal with multiple TimeseriesIds per one point.'
            ts_id = ts_id[0]
            ts_id.reference = point.name
            ts_id.isPointOf = self.name
            timeseries_ids.append(ts_id)
        if len(timeseries_ids) == 0:
            raise Exception(f'No timeseries points found associated with {self.name} in the graph.')

        return timeseries_ids

    def get_all_timeseries(self, time_frame, relationship='hasPoint'):
        """

        :param relationship: hasPoint is default because of timeseries storage conventions defined by the BrickSchema
        documentation
        :return:
        """
        ts_ids = self.get_timeseries_ids(relationship)
        connstr_res = self.g.query(
            """SELECT ?str WHERE { bldg:database bldg:connstring ?str}"""
        )
        list_ = self.unpack(connstr_res, ['str'])
        connstr = list_[0].name
        start, end = time_frame.tuple[0], time_frame.tuple[1]
        dict_ = {}
        for id in ts_ids:
            timestr = f'/timeseries?start_time={start}&end_time={end}'
            fullstr = connstr + id.name + timestr   #todo: better to use self.URI instead somehow
            s = get_timeseries(fullstr)
            ts = TimeseriesResponse(
                id=id.name,
                reference=id.reference,
                data=s,
                units=id.unit,
                isPointOf=id.isPointOf
            )
            dict_.update({id.reference: ts})

        self.last_response = dict_
        return dict_

    def join_last_response(self):
        """

        :return:
        """
        list_ = [x.data for x in self.last_response.values()]
        df = pd.concat(list_, axis=1)

        return df

class TimeseriesResponse():
    """

    """
    def __init__(self, **kwargs):
        """

        """
        self.id = None
        self.units = None
        self.reference = None
        self.isPointOf = None
        self.data = None
        self.__dict__.update(kwargs.copy())

class EntityList():
    """

    """
    def __init__(self, list_):
        self.list_ = list_

    def join_last_response(self):
        df = None
        for entity in self.list_:
            list_ = [x.data for x in entity.last_response.values()]
            colnames = [f'{entity.name}__{x}' for x in entity.last_response.keys()]
            df2 = pd.concat(list_, axis=1)
            df2.columns = colnames
            if df is not None:
                df = pd.concat([df, df2], axis=1)
            else:
                df = df2
        return df

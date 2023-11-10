"""Trying out

"""
from brickschema import Graph
from utils import BrickModel

# chiller power as a function of chiller on/off, ChW temps, and OAT
g = Graph(load_brick=True)
g.load_file('models/msl.ttl')
model = BrickModel(g)

# get chiller
chiller = model.get_entities(brick_class='Chiller')

# get timeseriesID of chiller power meter

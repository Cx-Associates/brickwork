"""Trying out

"""
from brickschema import Graph
from utils import BrickModel

# chiller power as a function of chiller on/off, ChW temps, and OAT
g = Graph(load_brick=True)
g.load_file('models/msl.ttl')
model = BrickModel(g)
model.time_frame = ('start', 'end')

# get chiller. I know there's only one chiller so I ask for the first result of the list.
chiller = model.get_entities(brick_class='Chiller')[0]

# get chiller power meter timeseries
ts_power_chiller = chiller.get_timeseries(chiller, 'isMeteredBy')

# get pumps
list_pumps = model.get_entities(brick_class='Pump')

pass
# get timeseriesID of chiller power meter

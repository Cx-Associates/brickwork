"""Trying out

"""
from utils import BrickModel

# chiller power as a function of chiller on/off, ChW temps, and OAT
ttl_path = 'models/msl.ttl'
model = BrickModel(ttl_path)

# store time_frame as a property of the model. This time frame (start time, end time) will be used for all queries of
# this graph unless explicitly overridden.
time_frame = ('2023-11-07T00:00:00', '2023-11-11T23:59:59')

# get chiller. I know there's only one chiller so I ask for the first result of the list.
chiller = model.get_entities(brick_class='Chiller')[0]

# get chiller power meter timeseries
ts_power_chiller = chiller.get_timeseries('isMeteredBy', time_frame)
ts_status_chiller = chiller.get_timeseries('isMeasuredBy', time_frame)

# get pumps
list_pumps = model.get_entities(brick_class='Pump')

pass
# get timeseriesID of chiller power meter

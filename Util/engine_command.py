
from collections import namedtuple

EngineCommand = namedtuple('EngineCommand',
                           'robot_id,'
                           'cruise_speed,'
                           'path,'
                           'move_type,'
                           'kick_type,'
                           'kick_force,'
                           'dribbler_state,'
                           'charge_kick,'
                           'target_orientation,'
                           'end_speed,'
                           'target_radius')

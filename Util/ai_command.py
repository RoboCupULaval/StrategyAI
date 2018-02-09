# Under MIT License, see LICENSE.txt

from collections import namedtuple


class AICommand(namedtuple('AICommand', 'robot_id target kick_type kick_force dribbler_active path '
                                        'cruise_speed end_speed')):

    __slots__ = ()

    def __new__(cls, robot_id, target=None, kick_type=None, kick_force=0, dribbler_active=False,
                path=None, cruise_speed=1, end_speed=0):
        return super().__new__(cls, robot_id, target, kick_type, kick_force, dribbler_active, path,
                               cruise_speed, end_speed)

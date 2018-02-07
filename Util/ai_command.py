# Under MIT License, see LICENSE.txt

from collections import namedtuple


class AICommand(namedtuple('AICommand', 'robot_id target kick_type kick_force dribbler_active')):

    __slots__ = ()

    def __new__(cls, robot_id, target=None, kick_type=None, kick_force=0, dribbler_active=False, command=None):
        return super().__new__(cls, robot_id, target, kick_type, kick_force, dribbler_active)

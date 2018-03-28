# Under MIT License, see LICENSE.txt

from collections import namedtuple

from Util.position import Position
from Util.pose import Pose
from Util.geometry import get_closest_point_on_segment, normalize

AICommand = namedtuple('AICommand', 'target,'
                                    'kick_type,'
                                    'kick_force,'
                                    'charge_kick,'
                                    'dribbler_active,'
                                    'cruise_speed,'
                                    'end_speed,'
                                    'ball_collision,'
                                    'pathfinder_on')


class CmdBuilder:

    def __init__(self):
        # Does are the defaults values of AICommand
        # A robot should stay idle with those value
        self._target = None
        self._kick_type = None
        self._kick_force = 0
        self._charge_kick = False
        self._dribbler_active = False
        self._cruise_speed = 0
        self._end_speed = 0
        self._ball_collision = True
        self._pathfinder_on = True

    def addMoveTo(self, target: [Pose, Position], cruise_speed=1, end_speed=0, ball_collision=True):
        assert isinstance(target, (Pose, Position))
        self._target = Pose(target) if isinstance(target, Position) else target
        self._cruise_speed = cruise_speed
        self._end_speed = end_speed
        self._ball_collision = ball_collision
        self._pathfinder_on = True
        return self

    def addKick(self, kick_force=1):
        self._kick_force = kick_force
        self._kick_type = 1  # For the moment we only have one type
        return self

    def addForceDribbler(self):
        self._dribbler_active = True
        return self

    def addChargeKicker(self):
        self._charge_kick = True
        return self

    def build(self):
        return AICommand(self._target,
                         self._kick_type,
                         self._kick_force,
                         self._charge_kick,
                         self._dribbler_active,
                         self._cruise_speed,
                         self._end_speed,
                         self._ball_collision,
                         self._pathfinder_on)


def MoveTo(target: [Pose, Position], cruise_speed=1, end_speed=0, ball_collision=True):
    return CmdBuilder().addMoveTo(target, cruise_speed, end_speed, ball_collision).build()


def GoBetween(position1: Position, position2: Position, target: Position, minimum_distance: [int, float]=0):
    delta = minimum_distance * normalize(position2 - position1)
    position1 = position1 + delta
    position2 = position2 - delta
    destination = get_closest_point_on_segment(target, position1, position2)
    dest_to_target = target - destination
    return CmdBuilder().addMoveTo(Pose(destination, dest_to_target.angle)).build()


Idle = CmdBuilder().build()

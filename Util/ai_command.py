# Under MIT License, see LICENSE.txt

from collections import namedtuple

from typing import Union

from Util.constant import KickForce, KickType
from Util.position import Position
from Util.pose import Pose

AICommand = namedtuple('AICommand', 'target,'
                                    'kick_type,'
                                    'kick_force,'
                                    'charge_kick,'
                                    'dribbler_active,'
                                    'cruise_speed,'
                                    'end_speed,'
                                    'ball_collision')

class CmdBuilder:

    def __init__(self):
        # Those are the defaults values of AICommand
        # A robot should stay idle with those value
        self._target = None
        self._kick_type = None
        self._kick_force = KickForce.NONE
        self._charge_kick = False
        self._dribbler_active = False
        self._cruise_speed = 0
        self._end_speed = 0
        self._ball_collision = True

    def addMoveTo(self, target: Union[Pose, Position], cruise_speed: float=1, end_speed: float=0, ball_collision: bool=True):
        assert isinstance(target, (Pose, Position))
        self._target = Pose(target) if isinstance(target, Position) else target
        self._cruise_speed = cruise_speed
        self._end_speed = end_speed
        self._ball_collision = ball_collision
        return self

    def addKick(self, kick_force:KickForce=KickForce.LOW):
        assert isinstance(kick_force, KickForce), 'kick_force should be a KickForce, not a {}'.format(type(kick_force))
        self._kick_force = kick_force
        self._kick_type = KickType.DIRECT
        return self

    def addForceDribbler(self):
        self._dribbler_active = True
        return self

    def addChargeKicker(self):
        self._charge_kick = True
        return self

    def build(self) -> AICommand:
        return AICommand(self._target,
                         self._kick_type,
                         self._kick_force,
                         self._charge_kick,
                         self._dribbler_active,
                         self._cruise_speed,
                         self._end_speed,
                         self._ball_collision)

def MoveTo(target: Union[Pose, Position], cruise_speed: float=1, end_speed: float=0, ball_collision: bool=True) -> AICommand:
    return CmdBuilder().addMoveTo(target, cruise_speed, end_speed, ball_collision).build()


Idle = CmdBuilder().build()

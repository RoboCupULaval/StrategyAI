# Under MIT License, see LICENSE.txt

from collections import namedtuple

from typing import Union

from Util.constant import KickForce, KickType, DribbleState
from Util.position import Position
from Util.pose import Pose
from Util.geometry import closest_point_on_segment, normalize

AICommand = namedtuple('AICommand', 'target,'
                                    'kick_type,'
                                    'kick_force,'
                                    'charge_kick,'
                                    'dribbler_state,'
                                    'cruise_speed,'
                                    'end_speed,'
                                    'ball_collision,'
                                    'way_points,'
                                    'enable_pathfinder')

class CmdBuilder:

    def __init__(self):
        # Those are the defaults values of AICommand
        # A robot should stay idle with those value
        self._target = None
        self._kick_type = None
        self._kick_force = KickForce.NONE
        self._charge_kick = False
        self._dribbler_state = DribbleState.AUTOMATIC
        self._cruise_speed = 0
        self._end_speed = 0
        self._ball_collision = True
        self._way_points = []
        self._enable_pathfinder = True

    def addMoveTo(self,
                  target: Union[Pose, Position],
                  cruise_speed: float=1,
                  end_speed: float=0,
                  ball_collision=True,
                  way_points=None,
                  enable_pathfinder=True):
        assert isinstance(target, (Pose, Position))

        self._target = Pose(target) if isinstance(target, Position) else target
        self._cruise_speed = cruise_speed
        self._end_speed = end_speed
        self._ball_collision = ball_collision
        self._enable_pathfinder = enable_pathfinder
        if way_points is not None:
            self._way_points = way_points
        return self

    def addKick(self, kick_force: KickForce=KickForce.LOW):
        assert isinstance(kick_force, KickForce), 'kick_force should be a KickForce, not a {}'.format(type(kick_force))
        self._kick_force = kick_force
        self._kick_type = KickType.DIRECT
        return self

    def addForceDribbler(self):
        self._dribbler_state = DribbleState.FORCE_SPIN
        return self

    def addStopDribbler(self):
        self._dribbler_state = DribbleState.FORCE_STOP
        return self

    def addChargeKicker(self):
        self._charge_kick = True
        return self

    def build(self) -> AICommand:
        return AICommand(target=self._target,
                         kick_type=self._kick_type,
                         kick_force=self._kick_force,
                         charge_kick=self._charge_kick,
                         dribbler_state=self._dribbler_state,
                         cruise_speed=self._cruise_speed,
                         end_speed=self._end_speed,
                         ball_collision=self._ball_collision,
                         way_points=self._way_points,
                         enable_pathfinder=self._enable_pathfinder)


def Kick(kick_force: KickForce=KickForce.LOW):
    return CmdBuilder().addKick(kick_force).build()


def MoveTo(target: Union[Pose, Position],
           cruise_speed: float=1,  # 1 m/s
           end_speed: float=0,
           ball_collision: bool=True,
           enable_pathfinder: bool=True) -> AICommand:
    return CmdBuilder().addMoveTo(target, cruise_speed, end_speed,
                                  ball_collision=ball_collision,
                                  enable_pathfinder=enable_pathfinder).build()


def GoBetween(position1: Position, position2: Position, target: Position, minimum_distance: float=0):
    delta = minimum_distance * normalize(position2 - position1)
    position1 = position1 + delta
    position2 = position2 - delta
    destination = closest_point_on_segment(target, position1, position2)
    dest_to_target = target - destination
    return CmdBuilder().addMoveTo(Pose(destination, dest_to_target.angle)).build()


Idle = CmdBuilder().build()

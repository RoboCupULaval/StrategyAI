# Under MIT License, see LICENSE.txt

from collections import namedtuple


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
        self.target = None
        self.kick_type = None
        self.kick_force = 0
        self.charge_kick = False
        self.dribbler_active = False
        self.cruise_speed = 0
        self.end_speed = 0
        self.ball_collision = True
        self.pathfinder_on = True

    def withMoveTo(self, target, cruise_speed=1, end_speed=0, ball_collision=True):
        self.target = target
        self.cruise_speed = cruise_speed
        self.end_speed = end_speed
        self.ball_collision = ball_collision
        self.pathfinder_on = True
        return self

    def withKick(self, kick_force=1):
        self.kick_force = kick_force
        self.kick_type = 1  # For the moment we only have one type
        return self

    def withForceDribbler(self):
        self.dribbler_active = True
        return self

    def withChargeKicker(self):
        self.charge_kick = True
        return self

    def build(self):
        return AICommand(self.target,
                         self.kick_type,
                         self.kick_force,
                         self.charge_kick,
                         self.dribbler_active,
                         self.cruise_speed,
                         self.end_speed,
                         self.ball_collision,
                         self.pathfinder_on)


Idle = CmdBuilder().build()

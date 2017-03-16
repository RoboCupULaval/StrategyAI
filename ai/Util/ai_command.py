from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from enum import Enum


class AICommandType(Enum):
    STOP = 0
    MOVE = 1
    KICK = 2


class AICommand(object):

    def __init__(self, p_robot_id, p_command=AICommandType.STOP, **other_args):
        self.robot_id = p_robot_id
        self.command = p_command
        self.dribbler_on = other_args.get("dribbler_on", 0)
        self.pathfinder_on = other_args.get("pathfinder_on", False)
        self.kick_strength = other_args.get("kick_strength", 0)
        self.charge_kick = other_args.get("charge_kick", False)
        self.pose_goal = other_args.get("pose_goal", Pose())
        self.speed = Pose()
        self.robot_speed = other_args.get("speed", 0)

        # this is for rotate around movement
        self.rotate_around_flag = other_args.get("rotate_around_flag", False)
        self.rotate_around_goal = other_args.get("rotate_around_goal", RotateAroundCommand())

        # this is for the pathfinder only no direct assignation
        self.path = []

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # Getter and setter here?

class RotateAroundCommand(object):
    """ Please, move me somewhere else"""
    def __init__(self, radius=0.0, direction=0.0, orientation=0.0, center_position=Position()):
        self.radius = radius
        self.direction = direction
        self.orientation = orientation
        self.center_position = center_position
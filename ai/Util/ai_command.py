from RULEngine.Util.Pose import Pose
from enum import Enum


class AICommandType(Enum):
    STOP = 0
    MOVE = 1
    KICK = 2


class AICommand(object):

    def __init__(self, p_robot_id, p_command=AICommandType.STOP, **other_args):
        self.robot_id = p_robot_id
        self.command = p_command
        self.dribbler_on = other_args.get("dribbler_on", False)
        self.pathfinder_on = other_args.get("pathfinder_on", False)
        self.kick_strength = other_args.get("kick_strength", 0)
        self.pose_goal = other_args.get("pose_goal", Pose())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    """getter and setters goes down here!"""

from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from enum import Enum


class AICommandType(Enum):
    STOP = 0
    MOVE = 1
    KICK = 2


class AICommand(object):
    """
    Sert a emmagasiner les états demandés par l'IA
    avant transformation en commandes d'envoie aux robots
    """
    def __init__(self, p_robot_id: int, p_command=AICommandType.STOP, **other_args):
        """
        Initialise.

        :param p_robot_id: (int) l'identifiant du robot
        :param p_command: (AICommandType) le type de AICommand
        :param other_args: (Dict) les flags et arguments à passer
        """
        self.robot_id = p_robot_id
        self.command = p_command
        self.dribbler_on = other_args.get("dribbler_on", 0)
        self.pathfinder_on = other_args.get("pathfinder_on", False)
        self.kick_strength = other_args.get("kick_strength", 0)
        self.charge_kick = other_args.get("charge_kick", False)
        self.pose_goal = other_args.get("pose_goal", Pose())
        self.speed = Pose()
        self.wheel_speed = (0,0,0,0)
        self.robot_speed = other_args.get("speed", 0)

        # set this flag to true if you only need speed regulation (The pose_goal will be in m/s)
        self.speed_flag = other_args.get("speed_flag", False)

        # this is for the pathfinder only no direct assignation
        self.path = []

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # Getter and setter here?


class RotateAroundCommand(object):
    """ Please, move me somewhere else"""
    # TODO what it wants ^
    def __init__(self, radius=0.0, direction=0.0, orientation=0.0, center_position=Position()):
        self.radius = radius
        self.direction = direction
        self.orientation = orientation
        self.center_position = center_position
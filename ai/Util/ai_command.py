from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from enum import Enum


class AICommandType(Enum):
    STOP = 0
    MOVE = 1
    MULTI = 2


class AIControlLoopType(Enum):
    OPEN = 0
    SPEED = 1
    POSITION = 2


class AICommand(object):
    """
    Sert a emmagasiner les états demandés par l'IA
    avant transformation en commandes d'envoie aux robots
    """
    def __init__(self, player: OurPlayer, command_type=AICommandType.STOP, **other_args):
        """
        Initialise.

        :param player: (OurPlayer) l'instance de notre player à qui appartient cette ai_commande
        :param p_command: (AICommandType) le type de AICommand
        :param other_args: (Dict) les flags et arguments à passer
        """
        assert isinstance(player, OurPlayer), "Création d'un ai_command sans passer une instance de OurPlayer."
        assert isinstance(command_type, AICommandType), "Besoin d'une AiCommandType!"
        self.player = player
        self.robot_id = player.id
        self.command = command_type
        self.dribbler_on = other_args.get("dribbler_on", 0)
        self.pathfinder_on = other_args.get("pathfinder_on", False)
        self.kick_strength = other_args.get("kick_strength", 0)
        self.charge_kick = other_args.get("charge_kick", False)
        self.kick = other_args.get("kick", False)
        self.pose_goal = other_args.get("pose_goal", Pose())
        self.speed = Pose()
        self.wheel_speed = (0, 0, 0, 0)
        self.cruise_speed = other_args.get("cruise_speed", 0.0001337)

        self.control_loop_type = other_args.get("control_loop_type", AIControlLoopType.POSITION)

        # this is for the pathfinder only no direct assignation
        self.path = []
        self.path_speeds = [0, 0]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # Getter and setter here?

    def __str__(self):
        return str(self.player.id)+"  " + str(self.player.team.team_color) + "  ->  "+str(id(self))


class RotateAroundCommand(object):
    """ Please, move me somewhere else"""
    # TODO what it wants ^
    def __init__(self, radius=0.0, direction=0.0, orientation=0.0, center_position=Position()):
        self.radius = radius
        self.direction = direction
        self.orientation = orientation
        self.center_position = center_position
# Under MIT License, see LICENSE.txt
from typing import List
import sys

from .pass_to_player import PassToPlayer
from .demo_follow_robot import DemoFollowRobot
from .do_kick import DoKick
from .measure_loop_delay import MeasureLoopDelay
from .rotate_around_position import RotateAroundPosition
from .rotate_around_ball import RotateAroundBall
from .Tactic import Tactic
from .bump import Bump
from .face_opponent import FaceOpponent
from .go_to_random_pose_in_zone import GoToRandomPosition
from .intercept import Intercept
from .position_for_pass import PositionForPass
from .robot_ident import RobotIdent
from .stay_away_from_ball import StayAwayFromBall
from .GoalKeeper import GoalKeeper
from .Stop import Stop
from .protect_zone import ProtectZone
from .demo_follow_ball import DemoFollowBall
from .go_to_position_no_pathfinder import GoToPositionNoPathfinder
from .go_to_position_pathfinder import GoToPositionPathfinder
from .go_kick import GoKick
from .face_target import FaceTarget
from .align_to_defense_wall import AlignToDefenseWall

try:
    from ai.STA.Tactic.joystick import Joystick
except ImportError:
    import warnings
    warnings.warn('Pygame is not installed, disabling Joystick tactic.', stacklevel=1)


class TacticBook(object):
    def __init__(self):
        """
        Initialise le dictionnaire des tactiques présentées au reste de l'IA.
        """
        self.tactic_book = {
            'AlignToDefenseWall': AlignToDefenseWall,
            'Bump': Bump,
            'DemoFollowBall': DemoFollowBall,
            'DemoFollowRobot': DemoFollowRobot,
            'DoKick': DoKick,
            'FaceOpponent': FaceOpponent,
            'FaceTarget': FaceTarget,
            'GoalKeeper': GoalKeeper,
            'GoKick': GoKick,
            'GoToPositionNoPathfinder': GoToPositionNoPathfinder,
            'GoToPositionPathfinder': GoToPositionPathfinder,
            'GoToRandomPosition': GoToRandomPosition,
            'Intercept': Intercept,
            'MeasureLoopDelay': MeasureLoopDelay,
            'PassToPlayer': PassToPlayer,
            'PositionForPass': PositionForPass,
            'ProtectZone': ProtectZone,
            'RobotIdent': RobotIdent,
            'RotateAroundBall': RotateAroundBall,
            'RotateAroundPosition': RotateAroundPosition,
            'StayAwayFromBall': StayAwayFromBall,
            'Stop': Stop,
        }
        if 'Joystick' in sys.modules:
            self.tactic_book['Joystick'] = Joystick

    def get_tactics_name_list(self) -> List[str]:
        """
        Retourne une liste des nomd des tactiques disponibles à l'IA.

        :return: (List[str]) une liste de string, les noms des tactiques disponibles.
        """
        return list(self.tactic_book.keys())

    def check_existance_tactic(self, tactic_name: str) -> bool:
        """
        Regarde que la tactique existe dans le livre des tactiques.

        :param tactic_name: (str) le nom de la tactique à évaluer l'existance.
        :return: (bool) true si la tactique existe dans le livre, false sinon.
        """
        assert isinstance(tactic_name, str)

        return tactic_name in self.tactic_book

    def get_tactic(self, tactic_name: str) -> Tactic:
        """
        Retourne une instance nouvelle de la tactique correspondant au nom passé.

        :param tactic_name: (str) le nom de la tactique à retourner
        :return: (Tactic) une nouvelle instance de la tactique demandé.
        """
        if self.check_existance_tactic(tactic_name):
            return self.tactic_book[tactic_name]
        return self.tactic_book['Stop']

# Under MIT License, see LICENSE.txt
from typing import List

import logging

from ai.STA.Tactic.place_ball import PlaceBall
from ai.STA.Tactic.face_target import FaceTarget
from ai.STA.Tactic.pass_to_player import PassToPlayer
from ai.STA.Tactic.demo_follow_robot import DemoFollowRobot
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.go_to_random_pose_in_zone import GoToRandomPosition
from ai.STA.Tactic.stay_away_from_ball import StayAwayFromBall
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.protect_zone import ProtectZone
from ai.STA.Tactic.demo_follow_ball import DemoFollowBall
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.go_kick import GoKick

# try:
#     from ai.STA.Tactic.joystick import Joystick
# except ImportError as e:
#     import warnings
#     warnings.warn(str(e), stacklevel=1)
#     warnings.warn('Pygame is not installed, disabling Joystick tactic.', stacklevel=1)


class TacticBook(object):
    def __init__(self):

        self.logger = logging.getLogger('TacticBook')

        self.tactic_book = {
            'PlaceBall' : PlaceBall,
            'FaceTarget': FaceTarget,
            'DemoFollowBall': DemoFollowBall,
            'DemoFollowRobot': DemoFollowRobot,
            'GoalKeeper': GoalKeeper,
            'GoKick': GoKick,
            'GoToPositionPathfinder': GoToPositionPathfinder,
            'GoToRandomPosition': GoToRandomPosition,
            'PassToPlayer': PassToPlayer,
            'ProtectZone': ProtectZone,
            'StayAwayFromBall': StayAwayFromBall,
            'Stop': Stop,
        }
        self.default_tactics = ['GoToPositionPathfinder',
                               'GoKick']

        for name, tactic_class in self.tactic_book.items():
            if name != tactic_class.__name__:
                raise TypeError("You give the wrong name to a tactic in tactic book: {} != {}".format(name, tactic_class.__name__))

        for name in self.default_tactics:
            if not name in self.tactic_book:
                raise TypeError("Default tactic ({}) is not in tactic book".format(name))

        # if 'Joystick' in sys.modules:
        #     self.tactic_book['Joystick'] = Joystick

    @property
    def tactics_name(self) -> List[str]:
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
        self.logger.error("Something asked for this non-existing tactic: {}".format(tactic_name))
        return self.tactic_book['Stop']

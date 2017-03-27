# Under MIT License, see LICENSE.txt
from typing import List

from ai.STA.Tactic.RotateAroundPosition import RotateAroundPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.test_turn_on_you import TestTurnOnYou
from ai.STA.Tactic.va_et_vient import VaEtVient
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.ProtectZone import ProtectZone
from ai.STA.Tactic.DemoFollowBall import DemoFollowBall
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.Joystick import Joystick


class TacticBook(object):
    def __init__(self):
        """
        Initialise le dictionnaire des tactiques présentées au reste de l'IA.
        """
        self.tactic_book = {'GoToPosition': GoToPosition,
                            'GoalKeeper': GoalKeeper,
                            'CoverZone': ProtectZone,
                            'GoGetBall': GoGetBall,
                            'DemoFollowBall': DemoFollowBall,
                            'Stop': Stop,
                            'GoToPositionNoPathfinder': GoToPositionNoPathfinder,
                            'GoToPositionPathfinder': GoToPositionPathfinder,
                            'GoKick': GoKick,
                            "TestTurnOnYou": TestTurnOnYou,
                            'RotateAroundPosition': RotateAroundPosition,
                            "VaEtVient": VaEtVient,
                            'Joystick': Joystick
                            }

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


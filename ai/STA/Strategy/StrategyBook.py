# Under MIT license, see LICENSE.txt

""" Livre des stratégies. """
from typing import List

from ai.STA.Strategy.DenfenseWall import DefenseWall
from ai.STA.Strategy.offense import Offense
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Strategy.indiana_jones import IndianaJones
from ai.STA.Strategy.HumanControl import HumanControl
from ai.STA.Strategy.SimpleDefense import SimpleDefense
from ai.STA.Strategy.SimpleOffense import SimpleOffense
from ai.STA.Strategy.DoNothing import DoNothing
from ai.STA.Strategy.WeirdmovementStrategy import WeirdmovementStrategy
from ai.STA.Strategy.TestTransitions import TestTransitions
from ai.STA.Strategy.PerpetualMovement import PerpetualMovement
#from ai.STA.Strategy.TestPasses import TestPasses
#from ai.STA.Strategy.TestRotateAround import TestRotateAround
from ai.STA.Strategy.passes_with_decisions import PassesWithDecisions
from ai.STA.Strategy.robocup_choreography import RobocupChoreography
from ai.STA.Strategy.bamba_follow import BambaFollow

class StrategyBook(object):
    """
        Cette classe est capable de récupérer les stratégies enregistrés dans
        la configuration des stratégies et de les exposer au Behavior Tree en
        charge de sélectionner la stratégie courante.
    """

    def __init__(self):
        """
        Initialise le dictionnaire des stratégies présentées au reste de l'IA.
        """
        self.strategy_book = {'SimpleDefense': SimpleDefense,
                              'SimpleOffense': SimpleOffense,
                              'Offense': Offense,
                              'HumanControl': HumanControl,
                              'DoNothing': DoNothing,
                              'TestTransitions': TestTransitions,
                              'PerpetualMovement': PerpetualMovement,
                              'WeirdmovementStrategy': WeirdmovementStrategy,
                              "IndianaJones": IndianaJones,
                              #"TestRotateAround": TestRotateAround,
                              #'TestPasses': TestPasses,
                              'RobocupChoreography': RobocupChoreography,
                              'BambaFollow': BambaFollow,
                              'PassesWithDecisions': PassesWithDecisions,
                              'DefenseWall': DefenseWall
                              }

    def get_strategies_name_list(self) -> List[str]:
        """
        Retourne une liste des noms des stratégies disponibles à l'IA.

        :return: (List[str]) une liste de string, les noms des stratégies disponibles.
        """
        return list(self.strategy_book.keys())

    def get_strategy(self, strategy_name: str) -> Strategy:
        """
        Retourne une instance nouvelle de la stratégie correspondant au nom passé.

        :param strategy_name: (str) le nom de la stratégie à retourner
        :return: (Tactic) une nouvelle instance de la stratégie demandé.
        """

        if self.check_existance_strategy(strategy_name):
            return self.strategy_book[strategy_name]
        return self.strategy_book['DoNothing']

    def check_existance_strategy(self, strategy_name: str) -> bool:
        """
        Regarde que la stratégie existe dans le livre des stratégies.

        :param strategy_name: (str) le nom de la stratégie à évaluer l'existance.
        :return: (bool) true si la stratégie existe dans le livre, false sinon.
        """
        assert isinstance(strategy_name, str)

        return strategy_name in self.strategy_book

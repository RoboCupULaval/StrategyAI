# Under MIT license, see LICENSE.txt

import logging
from typing import List, Dict

from ai.STA.Strategy.defense_wall_no_kick import DefenseWallNoKick
from ai.STA.Strategy.defense_wall import DefenseWall
from ai.STA.Strategy.direct_free_kick import DirectFreeKick
from ai.STA.Strategy.indirect_free_kick import IndirectFreeKick
from ai.STA.Strategy.offense import Offense
from ai.STA.Strategy.indiana_jones import IndianaJones
from ai.STA.Strategy.human_control import HumanControl
from ai.STA.Strategy.do_nothing import DoNothing
from ai.STA.Strategy.offense_kickoff import OffenseKickOff
from ai.STA.Strategy.passes_with_decisions import PassesWithDecisions
from ai.STA.Strategy.pathfinder_benchmark import PathfinderBenchmark
from ai.STA.Strategy.penalty_defense import PenaltyDefense
from ai.STA.Strategy.penalty_offense import PenaltyOffense
from ai.STA.Strategy.prepare_kickoff_defense import PrepareKickOffDefense
from ai.STA.Strategy.prepare_kickoff_offense import PrepareKickOffOffense
from ai.STA.Strategy.prepare_penalty_defense import PreparePenaltyDefense
from ai.STA.Strategy.prepare_penalty_offense import PreparePenaltyOffense
from ai.STA.Strategy.robocup_choreography import RobocupChoreography
from ai.STA.Strategy.bamba_follow import BambaFollow
from ai.STA.Strategy.stay_away import StayAway

__author__ = "Maxime Gagnon-Legault, and others"


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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.strategy_book = {'Offense': Offense,
                              'HumanControl': HumanControl,
                              'DoNothing': DoNothing,
                              "IndianaJones": IndianaJones,
                              'RobocupChoreography': RobocupChoreography,
                              'BambaFollow': BambaFollow,
                              'PassesWithDecisions': PassesWithDecisions,
                              'DefenseWall': DefenseWall,
                              'PathfinderBenchmark': PathfinderBenchmark,
                              'PrepareKickOffOffense': PrepareKickOffOffense,
                              'StayAway': StayAway,
                              'PrepareKickOffDefense': PrepareKickOffDefense,
                              'PenaltyDefense': PenaltyDefense,
                              'PenaltyOffense': PenaltyOffense,
                              'DirectFreeKick': DirectFreeKick,
                              'IndirectFreeKick': IndirectFreeKick,
                              'PreparePenaltyDefense': PreparePenaltyDefense,
                              'PreparePenaltyOffense': PreparePenaltyOffense,
                              'OffenseKickOff': OffenseKickOff,
                              'DefenseWallNoKick': DefenseWallNoKick,
                              }
        self.default_strategies = ['Offense',
                                   'DefenseWall']

        for name, strategy_class in self.strategy_book.items():
            if name != strategy_class.__name__:
                raise TypeError("You give the wrong name to a strategy in strategy book: {} != {}"
                                .format(name, strategy_class.__name__))

        for name in self.default_strategies:
            if name not in self.strategy_book:
                raise TypeError("Default strategy ({}) is not in strategy book".format(name))

    @property
    def strategies_name(self) -> List[str]:
        """
        Retourne une liste des noms des stratégies disponibles à l'IA.

        :return: (List[str]) une liste de string, les noms des stratégies disponibles.
        """
        return list(self.strategy_book)

    @property
    def strategies_required_roles(self) -> Dict[str, List[str]]:
        results = {}
        for name, strategy_class in self.strategy_book.items():
            results[name] = list([r.name for r in strategy_class.required_roles().keys()])
        return results

    def get_strategy(self, strategy_name: str):  # -> Strategy: Wrong return type
        """
        Retourne une instance nouvelle de la stratégie correspondant au nom passé.

        :param strategy_name: (str) le nom de la stratégie à retourner
        :return: (Tactic) une nouvelle instance de la stratégie demandé.
        """
        assert isinstance(strategy_name, str)

        if self.check_existance_strategy(strategy_name):
            return self.strategy_book[strategy_name]
        self.logger.error("Something asked for this non-existing strategy: {}".format(strategy_name))
        return self.strategy_book['DoNothing']

    def check_existance_strategy(self, strategy_name: str) -> bool:
        """
        Regarde que la stratégie existe dans le livre des stratégies.

        :param strategy_name: (str) le nom de la stratégie à évaluer l'existance.
        :return: (bool) true si la stratégie existe dans le livre, false sinon.
        """
        assert isinstance(strategy_name, str)

        return strategy_name in self.strategy_book

# Under MIT license, see LICENSE.txt

""" Livre des stratégies. """
from typing import List

from ai.STA.Strategy.defense_wall_3v3 import DefenseWall_3v3
from ai.STA.Strategy.defense_wall_no_kick import DefenseWallNoKick
from ai.STA.Strategy.defense_wall import DefenseWall
from ai.STA.Strategy.direct_free_kick import DirectFreeKick
from ai.STA.Strategy.indirect_free_kick import IndirectFreeKick
from ai.STA.Strategy.lineup import LineUp
from ai.STA.Strategy.offense import Offense
from ai.STA.Strategy.offense_3v3 import Offense_3v3
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Strategy.indiana_jones import IndianaJones
from ai.STA.Strategy.human_control import HumanControl
from ai.STA.Strategy.do_nothing import DoNothing
from ai.STA.Strategy.offense_kickoff import OffenseKickOff
from ai.STA.Strategy.passes_with_decisions import PassesWithDecisions
from ai.STA.Strategy.pathfinder_benchmark import Pathfinder_Benchmark
from ai.STA.Strategy.penalty_defense import PenaltyDefense
from ai.STA.Strategy.penalty_offense import PenaltyOffense
from ai.STA.Strategy.prepare_kickoff_defense import PrepareKickOffDefense
from ai.STA.Strategy.prepare_kickoff_offense import PrepareKickOffOffense
from ai.STA.Strategy.prepare_penalty_defense import PreparePenaltyDefense
from ai.STA.Strategy.prepare_penalty_offense import PreparePenaltyOffense
from ai.STA.Strategy.robocup_choreography import RobocupChoreography
from ai.STA.Strategy.bamba_follow import BambaFollow
from ai.STA.Strategy.stay_away import StayAway


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
        self.strategy_book = {'Offense': Offense,
                              'HumanControl': HumanControl,
                              'DoNothing': DoNothing,
                              "IndianaJones": IndianaJones,
                              'RobocupChoreography': RobocupChoreography,
                              'BambaFollow': BambaFollow,
                              'PassesWithDecisions': PassesWithDecisions,
                              'DefenseWall': DefenseWall,
                              'Pathfinder_Benchmark': Pathfinder_Benchmark,
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
                              'Offense_3v3': Offense_3v3,
                              'DefenseWall_3v3': DefenseWall_3v3,
                              'LineUp': LineUp
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

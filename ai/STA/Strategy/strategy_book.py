# Under MIT license, see LICENSE.txt

import logging
from typing import List, Dict, Type

from ai.STA.Strategy.smart_stop import SmartStop
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Strategy.ball_placement import BallPlacement
from ai.STA.Strategy.defense_wall_no_kick import DefenseWallNoKick
from ai.STA.Strategy.defense_wall import DefenseWall
from ai.STA.Strategy.direct_free_kick import DirectFreeKick
from ai.STA.Strategy.indirect_free_kick import IndirectFreeKick
from ai.STA.Strategy.lineup import LineUp
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
from ai.STA.Strategy.test_goal_keeper import TestGoalKeeper
from ai.STA.Strategy.test_passing import TestPassing

__author__ = "Maxime Gagnon-Legault, and others"


class StrategyBook:

    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.stop_strategy = DoNothing

        default_strategies = [Offense, DefenseWall]

        strategy_book = {TestPassing,
                         HumanControl,
                         IndianaJones,
                         RobocupChoreography,
                         BambaFollow,
                         PassesWithDecisions,
                         PathfinderBenchmark,
                         PrepareKickOffOffense,
                         StayAway,
                         PrepareKickOffDefense,
                         PenaltyDefense,
                         PenaltyOffense,
                         DirectFreeKick,
                         IndirectFreeKick,
                         PreparePenaltyDefense,
                         PreparePenaltyOffense,
                         OffenseKickOff,
                         DefenseWallNoKick,
                         BallPlacement,
                         TestGoalKeeper,
                         LineUp,
                         SmartStop,
                         self.stop_strategy,
                         *default_strategies,
                         }

        self.default_strategies = [strategy.name() for strategy in default_strategies]
        self.strategy_book = {strategy.name(): strategy for strategy in strategy_book}

    @property
    def strategies_name(self) -> List[str]:
        return list(self.strategy_book)

    @property
    def strategies_roles(self) -> Dict[str, Dict[str, List[str]]]:
        results = {}
        for name, strategy_class in self.strategy_book.items():
            assert isinstance(strategy_class.required_roles(), list), \
                "Strategy {} does not provide a list in it's required_roles()".format(name)
            assert isinstance(strategy_class.optional_roles(), list), \
                "Strategy {} does not provide a list in it's optional_roles()".format(name)
            results[name] = {"required_roles": list([r.name for r in strategy_class.required_roles()]),
                             "optional_roles": list([r.name for r in strategy_class.optional_roles()])}
        return results

    def get_strategy(self, strategy_name: str) -> Type[Strategy]:

        assert isinstance(strategy_name, str)

        if self.check_existance_strategy(strategy_name):
            return self.strategy_book[strategy_name]
        self.logger.error('A non-existing strategy was asked: {}'.format(strategy_name))
        return self.stop_strategy

    def check_existance_strategy(self, strategy_name: str) -> bool:
        assert isinstance(strategy_name, str)
        return strategy_name in self.strategy_book

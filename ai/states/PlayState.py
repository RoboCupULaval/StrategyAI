# Under MIT License, see LICENSE.txt

from ai.states.singleton import singleton

from ai.STA.Strategy.StrategyBook import StrategyBook
from ai.STA.Tactic.TacticBook import TacticBook


@singleton
class PlayState(object):

    def __init__(self):
        self.strategy_book = StrategyBook()
        self.tactic_book = TacticBook()
        self.current_strategy = None
        self.current_ai_commands = []
        self.ready_to_ship_robot_packet_list = []

    def set_strategy(self, strategy):
        assert self.strategy_book.check_existance_strategy(str(strategy))

        self.current_strategy = strategy

    def get_current_tactical_state(self):
        return self.current_strategy.get_current_state()

    def get_new_strategy(self, strategy_name):
        return self.strategy_book.get_strategy(strategy_name)

    def get_new_tactic(self, tactic_name):
        return self.tactic_book.get_tactic(tactic_name)

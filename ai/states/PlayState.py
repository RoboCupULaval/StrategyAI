from enum import Enum
from collections import namedtuple

from ai.STA.Strategy.StrategyBook import StrategyBook
from ai.STA.Tactic.TacticBook import TacticBook

STAStatus = Enum('boolean_enum', [('FREE', True), ('LOCKED', False)])

play = namedtuple("play", ["object", "status"])


class PlayState(object):

    def __init__(self):
        self.strategy_book = StrategyBook()
        self.tactic_book = TacticBook()
        self.current_strategy = play(None, STAStatus.FREE)
        self.current_tactics = [play(None, STAStatus.FREE) for i in range(6)]

    def set_strategy(self, strategy, status=STAStatus.FREE):
        assert self.strategy_book.check_existance_strategy(strategy)

        self.current_strategy = play(strategy, status)

    def set_tactic(self, player_id, tactic, status=STAStatus.FREE, args_list=None):
        assert self.tactic_book.check_existance_tactic(tactic)

        self.current_tactics[player_id] = play(tactic, status)

    def set_strategy_status(self, status=STAStatus.FREE):
        self.current_strategy = play(self.current_strategy.object, status)

    def set_tactic_status(self, player_id_list, status=STAStatus.FREE):
        for player_id in player_id_list:
            self.current_tactics[player_id] = play(self.current_tactics[player_id].object, status)

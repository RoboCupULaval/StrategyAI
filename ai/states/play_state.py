# Under MIT License, see LICENSE.txt

from typing import List, Tuple

from Util import Singleton
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Strategy.strategy_book import StrategyBook
from ai.STA.Tactic.tactic_book import TacticBook
from ai.states import GameState


class PlayState(metaclass=Singleton):

    def __init__(self):
        self.strategy_book = StrategyBook()
        self.tactic_book = TacticBook()
        self.autonomous_flag = False
        self._current_strategy = None

    @property
    def current_strategy(self):
        return self._current_strategy

    @current_strategy.setter
    def current_strategy(self, strategy_name: str):
        assert isinstance(strategy_name, str)

        strategy_class = self.strategy_book.get_strategy(strategy_name)
        self._current_strategy = strategy_class(GameState())

    def set_autonomous_flag(self, flag: bool) -> None:
        self.autonomous_flag = flag

    @property
    def current_tactical_state(self) -> List[Tuple[int, str, str, str]]:
        """
        Retourne le nom des tactics en cours dans la stratégie en cours
        :return: List[Tuple[int, str, str, str]] les informations actuelles des tactiques courantes
        """

        return self.current_strategy.get_current_state()

    def get_new_tactic(self, tactic_name: str):  # -> Callable[[GameState, Player, Pose, Any], Tactic]:
        """
        Retourne un callable sur la tactic spécifiée par le tactic_name.

        :param tactic_name: (str) le nom de la stratégie à retourner
        :return: Callable[[*args], Tactic] une Tactic non initialisé (non créer)
        """
        return self.tactic_book.get_tactic(tactic_name)

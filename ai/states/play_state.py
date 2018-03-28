# Under MIT License, see LICENSE.txt
import logging
from typing import List, Tuple, Callable, Dict

from Util import Pose
from ai.GameDomainObjects import Player

from ai.STA.Strategy.strategy_book import StrategyBook
from ai.STA.Tactic.tactic_book import TacticBook
from ai.states.game_state import GameState


class PlayState:

    def __init__(self):
        self.strategy_book = StrategyBook()
        self.tactic_book = TacticBook()
        self.game_state = GameState()
        self.autonomous_flag = False
        self._current_strategy = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def current_strategy(self):
        return self._current_strategy

    @current_strategy.setter
    def current_strategy(self, strategy_name: str):
        self.change_strategy(strategy_name)

    def change_strategy(self, strategy_name: str, role=None):
        assert isinstance(strategy_name, str)

        self.logger.debug("Switching to strategy '{}'".format(strategy_name))

        strategy_class = self.strategy_book.get_strategy(strategy_name)

        # Use default rule of the strategy
        if role is None:
            self.game_state.map_players_for_strategy(strategy_class)
        else: # Use role mapping from UI-debug
            self.game_state.map_players_to_roles_by_player_id(role)
            
        self._current_strategy = strategy_class(self.game_state)

    def set_autonomous_flag(self, flag: bool) -> None:
        self.autonomous_flag = flag

    @property
    def current_tactical_state(self) -> List[Tuple[Player, str, str, Pose]]:
        """
        Retourne le nom des tactics en cours dans la stratégie en cours
        :return: List[Tuple[int, str, str, str]] les informations actuelles des tactiques courantes
        """

        return self.current_strategy.get_current_state()

    def get_new_tactic(self, tactic_name: str) -> Callable:
        """
        Retourne un callable sur la tactic spécifiée par le tactic_name.

        :param tactic_name: (str) le nom de la stratégie à retourner
        :return: Callable[[*args], Tactic] une Tactic non initialisé (non créer)
        """
        return self.tactic_book.get_tactic(tactic_name)

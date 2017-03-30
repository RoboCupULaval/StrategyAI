# Under MIT License, see LICENSE.txt

from typing import List, Tuple, Callable, Any

from RULEngine.Util.Pose import Pose
from RULEngine.Util.singleton import Singleton
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Strategy.StrategyBook import StrategyBook
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.TacticBook import TacticBook
from ai.states.game_state import GameState


class PlayState(object, metaclass=Singleton):
    """
    Garde les éléments correspondant aux STA
    """
    def __init__(self):
        """
        initialise le PlayState
        """
        # Livres
        self.strategy_book = StrategyBook()
        self.tactic_book = TacticBook()

        self.current_strategy = None
        self.current_ai_commands = {}

    def set_strategy(self, strategy: Strategy) -> None:
        """
        applique un stratégie du STA à executer

        :param strategy: Strategy object déjà instancier, la stratégie à executer
        :return: None
        """
        assert self.strategy_book.check_existance_strategy(str(strategy))

        self.current_strategy = strategy

    def get_current_tactical_state(self) -> List[Tuple[int, str, str, str]]:
        """
        Retourne le nom des tactics en cours dans la stratégie en cours
        :return: List[Tuple[int, str, str, str]] les informations actuelles des tactiques courantes
        """

        return self.current_strategy.get_current_state()

    def get_new_strategy(self, strategy_name: str) -> Callable[[GameState], Strategy]:
        """
        Retourne un callable sur la stratégie spécifiée par le strategy_name.

        :param strategy_name: (str) le nom de la stratégie à retourner
        :return: Callable[[GameState], Strategy] une Stratégie non initialisé (non créer)
        """
        return self.strategy_book.get_strategy(strategy_name)

    def get_new_tactic(self, tactic_name: str) -> Callable[[GameState, int, Pose, Any], Tactic]:
        """
        Retourne un callable sur la tactic spécifiée par le tactic_name.

        :param tactic_name: (str) le nom de la stratégie à retourner
        :return: Callable[[*args], Tactic] une Tactic non initialisé (non créer)
        """
        return self.tactic_book.get_tactic(tactic_name)

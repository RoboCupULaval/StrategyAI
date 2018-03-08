# Under MIT License, see LICENSE.txt

from typing import List, Tuple

from Util import Singleton
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Strategy.strategy_book import StrategyBook
from ai.STA.Tactic.tactic_book import TacticBook


class PlayState(object, metaclass=Singleton):
    """
    Garde les éléments correspondant aux STA
    """
    def __init__(self):
        """
        initialise le PlayState
        """
        self.strategy_book = StrategyBook()
        self.tactic_book = TacticBook()
        self.autonomous_flag = False
        self.current_strategy = None

    def set_strategy(self, strategy: Strategy) -> None:
        """
        Applique un stratégie du STA à executer

        :param strategy: Strategy object déjà instancier, la stratégie à executer
        :return: None
        """
        print(strategy)
        assert self.strategy_book.check_existance_strategy(str(strategy))

        self.current_strategy = strategy

    def set_autonomous_flag(self, flag: bool) -> None:
        self.autonomous_flag = flag

    def get_current_tactical_state(self) -> List[Tuple[int, str, str, str]]:
        """
        Retourne le nom des tactics en cours dans la stratégie en cours
        :return: List[Tuple[int, str, str, str]] les informations actuelles des tactiques courantes
        """

        return self.current_strategy.get_current_state()

    def get_new_strategy(self, strategy_name: str):  # -> Callable[[GameState], Strategy]:
        """
        Retourne un callable sur la stratégie spécifiée par le strategy_name.

        :param strategy_name: (str) le nom de la stratégie à retourner
        :return: Callable[[GameState], Strategy] une Stratégie non initialisé (non créer)
        """
        return self.strategy_book.get_strategy(strategy_name)

    def get_new_tactic(self, tactic_name: str):  # -> Callable[[GameState, Player, Pose, Any], Tactic]:
        """
        Retourne un callable sur la tactic spécifiée par le tactic_name.

        :param tactic_name: (str) le nom de la stratégie à retourner
        :return: Callable[[*args], Tactic] une Tactic non initialisé (non créer)
        """
        return self.tactic_book.get_tactic(tactic_name)

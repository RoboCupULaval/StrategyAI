# Under MIT licence, see LICENCE.txt

from abc import abstractmethod

from Util import AICommand
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState


class Action:
    """
    Classe mère de toutes les actions
    """

    # noinspection PyUnreachableCode
    def __init__(self, game_state: GameState, player: Player):
        """
            :param game_state: L'état courant du jeu.
            :param player: (Player) instance du joueur qui execute l'action
        """
        assert isinstance(game_state, GameState), "action classe mère doit avoir un p_game_state objet GameState"
        assert isinstance(player, Player), "action classe mère doit avoir pour player une instance de Player"

        raise RuntimeError("Action are deprecated, use CmdBuilder instead.")
        self.game_state = game_state
        self.player = player

    @abstractmethod
    def exec(self) -> AICommand:
        """
        Calcul la prochaine action d'un joueur et mets l'aicommand construit dans le joueur.

        :return: AICommand
        """
        pass

    def __str__(self):
        return str(self.player) + " -> " + self.__class__.__name__

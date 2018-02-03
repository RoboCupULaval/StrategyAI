# Under MIT license, see LICENSE.txt

__author__ = 'Maxime Gagnon-Legault'


from Util.Pose import Pose
from Util import AICommand
from ai.GameDomainObjects import Player
from ai.STA.Action.Action import Action
from ai.states.game_state import GameState


class Grab(Action):
    def __init__(self, game_state: GameState, player: Player):
        """
            :param game_state: L'etat courant du jeu.
            :param player: Instance du joueur qui se deplace
        """
        Action.__init__(self, game_state, player)

    def exec(self) -> AICommand:
        ball = self.game_state.ball.position
        return AICommand(self.player.id, target=Pose(ball, self.player.pose.orientation).to_dict())

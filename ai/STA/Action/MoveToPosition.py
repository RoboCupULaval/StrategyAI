# Under MIT license, see LICENSE.txt

from Util import Pose, AICommand
from ai.GameDomainObjects import Player
from ai.STA.Action import Action
from ai.states import GameState


class MoveToPosition(Action):

    def __init__(self, game_state: GameState, player: Player, destination: Pose):
        Action.__init__(self, game_state, player)
        assert isinstance(destination, Pose)

        self.destination = destination

    def exec(self):
        return AICommand(self.player.id, self.destination)

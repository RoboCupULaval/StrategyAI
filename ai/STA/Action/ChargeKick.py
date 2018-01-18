# Under MIT license, see LICENSE.txt

from RULEngine.GameDomainObjects.player import Player
from Util import AICommand
from ai.STA.Action.Action import Action
from ai.states.game_state import GameState

__author__ = 'Robocup ULaval'


class ChargeKick(Action):

    def __init__(self, game_state: GameState, player: Player):
        Action.__init__(self, game_state, player)

    def exec(self):
        return AICommand(self.player, charge_kick=True)

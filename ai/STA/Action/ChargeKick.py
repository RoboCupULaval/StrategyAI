# Under MIT license, see LICENSE.txt

from RULEngine.Game.OurPlayer import OurPlayer
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand

__author__ = 'Robocup ULaval'


class ChargeKick(Action):

    def __init__(self, game_state: GameState, player: OurPlayer):
        Action.__init__(self, game_state, player)

    def exec(self):
        return AICommand(self.player, charge_kick=True)

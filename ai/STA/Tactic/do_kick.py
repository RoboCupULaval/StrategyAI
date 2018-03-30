# Under MIT license, see LICENSE.txt
from typing import List

from Util import Pose
from Util.ai_command import CmdBuilder
from ai.GameDomainObjects import Player

from ai.STA.Action.Kick import Kick
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class DoKick(Tactic):
    """
    Use to test if you can kick with a robot for debugging purposes
    """
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.kick
        self.next_state = self.kick
        self.kick_force = 10

    def kick(self):
        self.next_state = self.halt
        return CmdBuilder().addKick(kick_force=self.kick_force).build()

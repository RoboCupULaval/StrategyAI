# Under MIT license, see LICENSE.txt
from typing import List

from ai.STA.Action.Kick import Kick
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.states.game_state import GameState
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags


class DoKick(Tactic):
    """
    Use to test if you can kick with a robot for debugging purposes
    """
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.kick
        self.next_state = self.kick
        self.kick_force = 10

    def kick(self):
        self.next_state = self.halt
        return Kick(self.game_state, self.player, self.kick_force)


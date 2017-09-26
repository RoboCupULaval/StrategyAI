# Under MIT license, see LICENSE.txt
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.states.game_state import GameState
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommand, AICommandType


class FaceTarget(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.next_state = self.exec
        self.player_position = player.pose.position

    def exec(self):
        self.status_flag = Flags.WIP
        target_orientation = (self.target.position - self.player.pose.position).angle()
        return AICommand(self.player, AICommandType.MOVE, pose_goal=Pose(self.player_position, target_orientation))


# Under MIT license, see LICENSE.txt
from typing import List

from Util import Pose
from Util.ai_command_shit import AICommand, AICommandType
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class FaceTarget(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.next_state = self.exec
        self.player_position = player.pose.position

    def exec(self):
        self.status_flag = Flags.WIP
        target_orientation = (self.target.position - self.player.pose.position).angle()
        return AICommand(self.player, AICommandType.MOVE, pose_goal=Pose(self.player_position, target_orientation))


from typing import List

from Debug.debug_command_factory import DebugCommandFactory, VIOLET
from Util import Pose, Position
from Util.ai_command import CmdBuilder, MoveTo
from Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT
from Util.geometry import compare_angle
from ai.GameDomainObjects.player import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class TacticTest(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose,
                 args: List[str]=None):
        super().__init__(game_state, player, target, args)

        self.origin = player.pose
        self.current_state = self.move
        self.next_state = self.move
        self.target = target

    def move(self):
        if self.check_success(self.target):
            self.next_state = self.move_back
        return MoveTo(self.target)

    def move_back(self):
        if self.check_success(self.origin):
            self.next_state = self.halt
        return MoveTo(self.origin)

    def check_success(self, target: Pose):
        distance = (self.player.pose - target.position).norm
        return (distance < POSITION_DEADZONE) and compare_angle(self.player.pose.orientation,
                                                                target.orientation, abs_tol=ANGLE_TO_HALT)
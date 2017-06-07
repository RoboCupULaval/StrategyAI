# Under MIT license, see LICENSE.txt
from typing import List
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.rotate_around import RotateAround
from ai.states.game_state import GameState


class RotateAroundPosition(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose, args: List[str]=None):
        super().__init__(game_state, player, target, args)

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP
        ball = self.game_state.get_ball_position().conv_2_np()
        target = self.target.position.conv_2_np()
        ball_to_target = target - ball
        orientation = np.arctan2(ball_to_target[1], ball_to_target[0])
        next_action = RotateAround(self.game_state, self.player, Pose(Position.from_np(ball), orientation), 90)
        return next_action.exec()

    def check_success(self):
        return False

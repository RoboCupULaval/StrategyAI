# Under MIT license, see LICENSE.txt
import numpy as np

from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.rotate_around import RotateAround
from ai.Util.ai_command import RotateAroundCommand
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import POSITION_DEADZONE


class RotateAroundPosition(Tactic):
    def __init__(self, game_state, player_id, target, args):
        super().__init__(game_state, player_id, target, args)
        self.status_flag = Flags.INIT
        self.target = target
        self.player_id = player_id

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP
        ball = self.game_state.get_ball_position().conv_2_np()
        target = self.target.position.conv_2_np()
        ball_to_target = target - ball
        orientation = np.arctan2(ball_to_target[1], ball_to_target[0])
        next_action = RotateAround(self.game_state, self.player_id, Pose(Position.from_np(ball), orientation), 90)
        return next_action.exec()

    def check_success(self):
        return False

# Under MIT license, see LICENSE.txt

import math as m

from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.MoveToPosition import MoveToPosition
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT


class GoToPositionNoPathfinder(Tactic):
    def __init__(self, p_game_state, player_id, target, args=None,):
        super().__init__(p_game_state, player_id, target, args)
        self.target = target
        self.status_flag = Flags.INIT

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        next_action = MoveToPosition(self.game_state, self.player_id, self.target)
        return next_action.exec()

    def check_success(self):
        player_pose = self.game_state.get_player_pose(player_id=self.player_id)
        distance = get_distance(player_pose.position, self.target.position)
        if distance < POSITION_DEADZONE and \
                m.fabs(player_pose.orientation - self.target.orientation) <= 2*ANGLE_TO_HALT:
            return True
        return False

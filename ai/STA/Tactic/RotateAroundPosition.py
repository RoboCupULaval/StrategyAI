# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.RotateArround import RotateAround
from ai.Util.ai_command import RotateAroundCommand
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import POSITION_DEADZONE


class RotateAroundPosition(Tactic):
    def __init__(self, p_game_state, player_id, target):
        super().__init__(p_game_state, player_id)
        self.rotate_around_cmd = RotateAroundCommand(10, 3.14/4, 3.14/4, target.position)
        self.status_flag = Flags.INIT

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        next_action = RotateAround(self.game_state, self.player_id, self.rotate_around_cmd)
        return next_action.exec()

    def check_success(self):
        return False

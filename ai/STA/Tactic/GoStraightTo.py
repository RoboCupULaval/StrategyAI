# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.MoveStraightTo import MoveStraightTo
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import POSITION_DEADZONE


class GoStraightTo(Tactic):
    def __init__(self, p_game_state, player_id, target):
        super().__init__(p_game_state, player_id)
        self.target = target
        self.status_flag = Flags.INIT

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        next_action = MoveStraightTo(self.game_state, self.player_id, self.target)
        return next_action.exec()

    def check_success(self):
        player_position = self.game_state.get_player_position(player_id=self.player_id)
        distance = get_distance(player_position, self.target.position)
        if distance < POSITION_DEADZONE:
            return True
        return False

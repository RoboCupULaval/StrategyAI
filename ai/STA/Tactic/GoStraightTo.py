# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . import tactic_constants
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Action.MoveStraightTo import MoveStraightTo
from ai.Util.types import AICommand


class GoStraightTo(Tactic):
    def __init__(self, p_game_state, player_id, target):
        super().__init__(p_game_state, player_id)
        self.target = target
        self.status_flag = tactic_constants.SUCCESS

    def exec(self):
        next_action = MoveStraightTo(self.game_state, self.player_id, self.target)
        return next_action.exec()

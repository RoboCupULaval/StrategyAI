# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . import tactic_constants
from RULEngine.Util.constant import PLAYER_PER_TEAM


class Stop(Tactic):
    def __init__(self, game_state, player_id, *args, **kwargs):
        super().__init__(game_state, player_id)
        self.status_flag = tactic_constants.SUCCESS

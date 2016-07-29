# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . import tactic_constants
from RULEngine.Util.constant import PLAYER_PER_TEAM


class Stop(Tactic):
    def __init__(self, p_info_manager, p_player_id):
        super().__init__(p_info_manager)
        assert isinstance(p_player_id, int)
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        self.player_id = p_player_id
        self.status_flag = tactic_constants.SUCCESS

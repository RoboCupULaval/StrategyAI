# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . import tactic_constants
from RULEngine.Util.constant import PLAYER_PER_TEAM


class Stop(Tactic):
    def __init__(self, p_gamestatemanager, p_playmanager, player_id, *args, **kwargs):
        super().__init__(p_gamestatemanager, p_playmanager, player_id)
        self.status_flag = tactic_constants.SUCCESS

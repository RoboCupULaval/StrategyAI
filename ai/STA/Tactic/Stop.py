# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . tactic_constants import Flags


class Stop(Tactic):
    def __init__(self, game_state, player_id, *args, **kwargs):
        super().__init__(game_state, player_id)
        self.status_flag = Flags.SUCCESS

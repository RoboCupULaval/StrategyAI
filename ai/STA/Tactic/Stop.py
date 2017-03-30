# Under MIT license, see LICENSE.txt
from RULEngine.Util.Pose import Pose
from .Tactic import Tactic
from . tactic_constants import Flags


class Stop(Tactic):
    def __init__(self, game_state, player_id, target=Pose(), args=None):
        super().__init__(game_state, player_id, target, args)
        self.status_flag = Flags.SUCCESS

# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.MoveStraightTo import MoveStraightTo
#TODO FIXME For the love of god change the place of this helper function!!!!!!!
from RULEngine.Util.geometry import get_distance

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
        player_pose = self.game_state.get_player_pose(player_id=self.player_id)
        distance = get_distance(player_pose.position, self.target.position)
        #FIXME thank tou
        if distance < 50:
            return True
        return False

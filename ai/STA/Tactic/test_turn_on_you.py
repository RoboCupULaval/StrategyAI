# Under MIT license, see LICENSE.txt
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Action.AllStar import AllStar
from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.MoveToPosition import MoveToPosition
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import POSITION_DEADZONE


class TestTurnOnYou(Tactic):
    def __init__(self, p_game_state, player_id):
        super().__init__(p_game_state, player_id)
        self.status_flag = Flags.INIT
        self.next_state = exec

    def exec(self):
        self.status_flag = Flags.WIP
        next_action = MoveToPosition(self.game_state, self.player_id,
                                     Pose(self.game_state.get_player_position(self.player_id), 3.14))
        return next_action.exec()


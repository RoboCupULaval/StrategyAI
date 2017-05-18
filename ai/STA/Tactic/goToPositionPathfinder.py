# Under MIT license, see LICENSE.txt

from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from RULEngine.Util.geometry import get_distance


class GoToPositionPathfinder(Tactic):
    def __init__(self, p_game_state, player_id, target, args=None):
        super().__init__(p_game_state, player_id, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        if args is not None:
            self.cruise_speed = float(args[0])
        else:
            self.cruise_speed = 1

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        next_action = PathfindToPosition(self.game_state, self.player_id,
                                         self.target, speed=self.cruise_speed)
        return next_action.exec()

    def check_success(self):
        player_position = \
            self.game_state.get_player_position(player_id=self.player_id)
        distance = get_distance(player_position, self.target.position)
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False

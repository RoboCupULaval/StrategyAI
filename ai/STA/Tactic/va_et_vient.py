from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags


class VaEtVient(Tactic):
    def __init__(self, p_game_state, player_id, target=Pose(), args=None):
        super().__init__(p_game_state, player_id, target, args)
        self.status_flag = Flags.INIT
        self.start = self.game_state.get_player_pose(self.player_id)
        self.end = Pose(position=self.target.position, orientation=0)
        self.debug = DebugInterface()

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.WIP
            self.switch_target()
        else:
            self.status_flag = Flags.WIP

        next_action = PathfindToPosition(self.game_state, self.player_id, self.target)
        return next_action.exec()

    def switch_target(self):
        player_position = self.game_state.get_player_position(self.player_id)
        distance_end = get_distance(player_position, self.end.position)
        distance_start = get_distance(player_position, self.start.position)
        if distance_end < distance_start:
            self.target = self.start
        else:
            self.target = self.end

    def check_success(self):
        player_position = self.game_state.get_player_position(self.player_id)

        distance = get_distance(player_position, self.target.position)
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False

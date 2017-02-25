from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags


class VaEtVient(Tactic):
    def __init__(self, p_game_state, player_id, target=Pose()):
        super().__init__(p_game_state, player_id)
        self.status_flag = Flags.INIT
        self.goal_left = (Pose(Position(self.game_state.const["FIELD_GOAL_YELLOW_X_LEFT"], 0), 0))
        self.goal_right = (Pose(Position(self.game_state.const["FIELD_GOAL_BLUE_X_RIGHT"], 0), 0))
        self.set_closer_goal()
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
        distance_left = get_distance(player_position, self.goal_left.position)
        distance_right = get_distance(player_position, self.goal_right.position)
        if distance_left < distance_right:
            self.target = self.goal_right
        else:
            self.target = self.goal_left

    def set_closer_goal(self):
        player_position = self.game_state.get_player_position(self.player_id)
        distance_left = get_distance(player_position, self.goal_left.position)
        distance_right = get_distance(player_position, self.goal_right.position)
        if distance_left < distance_right:
            self.target = self.goal_left
        else:
            self.target = self.goal_right

    def check_success(self):
        player_position = self.game_state.get_player_position(self.player_id)

        distance = get_distance(player_position, self.target.position)
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False

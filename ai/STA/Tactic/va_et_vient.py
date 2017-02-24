from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags


class VaEtVient(Tactic):
    def __init__(self, p_game_state, player_id):
        super().__init__(p_game_state, player_id)
        self.status_flag = Flags.INIT
        self.set_closer_goal()

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        next_action = PathfindToPosition(self.game_state, self.player_id, self.target)
        return next_action.exec()

    def set_closer_goal(self):
        player_position = self.game_state.get_player_position(self.player_id)
        goal_left = Position(self.game_state.const["FIELD_GOAL_YELLOW_X_LEFT"], 0)
        goal_right = Position(self.game_state.const["FIELD_GOAL_BLUE_X_RIGHT"], 0)
        distance_left = get_distance(player_position, goal_left)
        distance_right = get_distance(player_position, goal_right)
        if distance_left < distance_right:
            self.target = goal_left
        else:
            self.target = goal_right

    def set_other_goal


    def check_success(self):
        player_position = self.game_state.get_player_position(self.player_id)

        distance = get_distance(player_position, self.target)
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False

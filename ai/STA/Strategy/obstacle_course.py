# Under MIT License, see LICENSE.txt

from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.Stop import Stop
from RULEngine.Util.Pose import Position, Pose
from ai.STA.Tactic.tactic_constants import Flags
from functools import partial


class ObstacleCourse(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        goal_left = (Pose(Position(self.game_state.const["FIELD_GOAL_YELLOW_X_LEFT"], 0), 0))
        goal_right = (Pose(Position(self.game_state.const["FIELD_GOAL_BLUE_X_RIGHT"], 0), 0))
        y_down = self.game_state.const["FIELD_Y_BOTTOM"] + 200
        y_top = self.game_state.const["FIELD_Y_TOP"] - 200
        x_right = self.game_state.const["FIELD_X_RIGHT"]
        x_left = self.game_state.const["FIELD_X_LEFT"]

        self.add_tactic(0, GoToPositionNoPathfinder(self.game_state, 0, Pose(Position(x_left/2, y_top))))
        self.add_tactic(0, GoToPositionNoPathfinder(self.game_state, 0, Pose(Position(x_left/2, y_down))))
        self.add_condition(0, 0, 1, partial(self.condition, 0))
        self.add_condition(0, 1, 0, partial(self.condition, 0))

        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(x_right/2, y_top))))
        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(x_right/2, y_down))))
        self.add_condition(1, 0, 1, partial(self.condition, 1))
        self.add_condition(1, 1, 0, partial(self.condition, 1))

        self.add_tactic(4, Stop(self.game_state, 4))
        self.add_tactic(4, GoToPositionNoPathfinder(self.game_state, 4, Pose(Position(x_left/2, y_top))))
        self.add_tactic(4, GoToPositionNoPathfinder(self.game_state, 4, Pose(Position(x_left/2, y_down))))
        self.add_condition(4, 1, 1, partial(self.condition, 4))
        self.add_condition(4, 1, 0, partial(self.condition, 4))

        self.add_tactic(3, Stop(self.game_state, 3))
        self.add_tactic(5, Stop(self.game_state, 5))
        self.add_tactic(2, Stop(self.game_state, 2))

    def condition(self, i):
        return self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS


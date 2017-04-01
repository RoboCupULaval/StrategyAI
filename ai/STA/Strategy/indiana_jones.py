# Under MIT License, see LICENSE.txt

from functools import partial

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags


class IndianaJones(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        # ID Robot Indiana Jones : 0
        indiana_ID = 4
        # ID Robot obstacles mouvants : 1 et 2
        obs_left_ID = 2
        obs_right_ID = 3
        # Positions objectifs d'Indiana Jones
        goal_left = (Pose(Position(self.game_state.const["FIELD_GOAL_YELLOW_X_LEFT"], 0), 0))
        goal_right = (Pose(Position(self.game_state.const["FIELD_GOAL_BLUE_X_RIGHT"], 0), 0))

        # Positions objectifs des obstacles
        y_down = self.game_state.const["FIELD_Y_BOTTOM"] + 500
        y_top = self.game_state.const["FIELD_Y_TOP"] - 500
        x_left = self.game_state.const["FIELD_X_LEFT"] + 500
        x_right = self.game_state.const["FIELD_X_RIGHT"] - 500


        self.add_tactic(indiana_ID, GoToPositionPathfinder(self.game_state, indiana_ID, goal_left))
        self.add_tactic(indiana_ID, GoToPositionPathfinder(self.game_state, indiana_ID, goal_right))
        self.add_condition(indiana_ID, 0, 1, partial(self.condition, indiana_ID))
        self.add_condition(indiana_ID, 1, 0, partial(self.condition, indiana_ID))

        self.add_tactic(obs_left_ID, GoToPositionPathfinder(self.game_state, obs_left_ID, Pose(Position(x_left/2, y_top))))
        self.add_tactic(obs_left_ID, GoToPositionPathfinder(self.game_state, obs_left_ID, Pose(Position(x_left/2, y_down))))
        self.add_condition(obs_left_ID, 0, 1, partial(self.condition, obs_left_ID))
        self.add_condition(obs_left_ID, 1, 0, partial(self.condition, obs_left_ID))

        self.add_tactic(obs_right_ID, GoToPositionPathfinder(self.game_state, obs_right_ID, Pose(Position(x_right/2, y_top))))
        self.add_tactic(obs_right_ID, GoToPositionPathfinder(self.game_state, obs_right_ID, Pose(Position(x_right/2, y_down))))
        self.add_condition(obs_right_ID, 0, 1, partial(self.condition, obs_right_ID))
        self.add_condition(obs_right_ID, 1, 0, partial(self.condition, obs_right_ID))

        for i in range(PLAYER_PER_TEAM):
            if not (i == indiana_ID or i == obs_left_ID or i == obs_right_ID):
                self.add_tactic(i, Stop(self.game_state, i))

        print("{} -- {} \n {} -- {}".format(y_down, y_top, x_right, x_left))

    def condition(self, i):
        print(i, self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS)
        return self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS


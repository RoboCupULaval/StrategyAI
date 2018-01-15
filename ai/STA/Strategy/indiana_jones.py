# Under MIT License, see LICENSE.txt

from functools import partial

from Util.Pose import Position, Pose
from Util.role import Role
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags


class IndianaJones(Strategy):

    def __init__(self, game_state, hard_code=True):
        super().__init__(game_state)
        # ID Robot Indiana Jones : 0
        # ID Robot obstacles mouvants : 1 et 2
        if hard_code:
            game_state.map_players_to_roles_by_player_id({
                Role.FIRST_DEFENCE: 3,
                Role.MIDDLE: 4,
                Role.SECOND_DEFENCE: 5,
            })
        indiana = self.game_state.get_player_by_role(Role.MIDDLE)
        indiana_role = Role.MIDDLE
        obs_right = self.game_state.get_player_by_role(Role.FIRST_DEFENCE)
        obs_right_role = Role.FIRST_DEFENCE
        obs_left = self.game_state.get_player_by_role(Role.SECOND_DEFENCE)
        obs_left_role = Role.SECOND_DEFENCE

        # TODO: The position must be update to fit to the current field
        # Positions objectifs d'Indiana Jones
        goal_left = (Pose(Position(self.game_state.const["FIELD_OUR_GOAL_X_INTERNAL"], 0), 0))
        goal_right = (Pose(Position(self.game_state.const["FIELD_THEIR_GOAL_X_INTERNAL"], 0), 0))

        # Positions objectifs des obstacles
        y_down = self.game_state.const["FIELD_Y_BOTTOM"] + 500
        y_top = self.game_state.const["FIELD_Y_TOP"] - 500
        x_left = self.game_state.const["FIELD_X_LEFT"] + 500
        x_right = self.game_state.const["FIELD_X_RIGHT"] - 500

        self.add_tactic(indiana_role, GoToPositionPathfinder(self.game_state, indiana, goal_left))
        self.add_tactic(indiana_role, GoToPositionPathfinder(self.game_state, indiana, goal_right))
        self.add_condition(indiana_role, 0, 1, partial(self.condition, indiana_role))
        self.add_condition(indiana_role, 1, 0, partial(self.condition, indiana_role))

        self.add_tactic(obs_left_role, GoToPositionPathfinder(self.game_state, obs_left,
                                                            Pose(Position(x_left/2, y_top))))
        self.add_tactic(obs_left_role, GoToPositionPathfinder(self.game_state, obs_left,
                                                            Pose(Position(x_left/2, y_down))))
        self.add_condition(obs_left_role, 0, 1, partial(self.condition, obs_left_role))
        self.add_condition(obs_left_role, 1, 0, partial(self.condition, obs_left_role))

        self.add_tactic(obs_right_role, GoToPositionPathfinder(self.game_state,
                                                             obs_right, Pose(Position(x_right/2, y_top))))
        self.add_tactic(obs_right_role, GoToPositionPathfinder(self.game_state,
                                                             obs_right, Pose(Position(x_right/2, y_down))))
        self.add_condition(obs_right_role, 0, 1, partial(self.condition, obs_right_role))
        self.add_condition(obs_right_role, 1, 0, partial(self.condition, obs_right_role))

    def condition(self, i):
        return self.roles_graph[i].get_current_tactic().status_flag == Flags.SUCCESS


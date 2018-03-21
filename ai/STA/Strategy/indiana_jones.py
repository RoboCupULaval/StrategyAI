# Under MIT License, see LICENSE.txt

from functools import partial

from Util.pose import Position, Pose
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
                Role.SECOND_DEFENCE: 6,
            })
        indiana = self.game_state.get_player_by_role(Role.MIDDLE)
        indiana_role = Role.MIDDLE
        obs_right = self.game_state.get_player_by_role(Role.FIRST_DEFENCE)
        obs_right_role = Role.FIRST_DEFENCE
        obs_left = self.game_state.get_player_by_role(Role.SECOND_DEFENCE)
        obs_left_role = Role.SECOND_DEFENCE

        # Positions objectifs d'Indiana Jones
        goal_left = (Pose(Position(self.game_state.const["FIELD_OUR_GOAL_X_INTERNAL"], 0), self.game_state.get_player_by_role(indiana_role).pose.orientation))
        goal_right = (Pose(Position(self.game_state.const["FIELD_THEIR_GOAL_X_INTERNAL"], 0), self.game_state.get_player_by_role(indiana_role).pose.orientation))

        # Positions objectifs des obstacles
        y_bottom = self.game_state.const["FIELD_Y_BOTTOM"] + 500
        y_top = self.game_state.const["FIELD_Y_TOP"] - 500
        x_left = self.game_state.const["FIELD_X_LEFT"] + 500
        x_right = self.game_state.const["FIELD_X_RIGHT"] - 500

        node_go_to_goal_left = self.create_node(indiana_role, GoToPositionPathfinder(self.game_state, indiana, goal_left, cruise_speed=2))
        node_go_to_goal_right = self.create_node(indiana_role, GoToPositionPathfinder(self.game_state, indiana, goal_right, cruise_speed=2))

        indiana_succeeded = partial(self.current_tactic_succeed, indiana_role)

        node_go_to_goal_left.connect_to(node_go_to_goal_right, when=indiana_succeeded)
        node_go_to_goal_right.connect_to(node_go_to_goal_left, when=indiana_succeeded)

        node_go_to_top_left = self.create_node(obs_left_role, GoToPositionPathfinder(self.game_state, obs_left,
                                                            Pose(Position(x_left/2, y_top),
                                                                 self.game_state.get_player_by_role(obs_left_role).pose.orientation), cruise_speed=2))
        node_go_to_bottom_left = self.create_node(obs_left_role, GoToPositionPathfinder(self.game_state, obs_left,
                                                            Pose(Position(x_left/2, y_bottom), self.game_state.get_player_by_role(obs_left_role).pose.orientation)))
        obs_left_role_succeeded = partial(self.current_tactic_succeed, obs_left_role)

        node_go_to_top_left.connect_to(node_go_to_bottom_left, when=obs_left_role_succeeded)
        node_go_to_bottom_left.connect_to(node_go_to_top_left, when=obs_left_role_succeeded)

        node_go_to_top_right = self.create_node(obs_right_role, GoToPositionPathfinder(self.game_state,
                                                             obs_right, Pose(Position(x_right/2, y_top), self.game_state.get_player_by_role(obs_right_role).pose.orientation), cruise_speed=2))
        node_go_to_bottom_right = self.create_node(obs_right_role, GoToPositionPathfinder(self.game_state,
                                                             obs_right, Pose(Position(x_right/2, y_bottom), self.game_state.get_player_by_role(obs_right_role).pose.orientation), cruise_speed=2))
        obs_right_role_succeeded = partial(self.current_tactic_succeed, obs_right_role)

        node_go_to_top_right.connect_to(node_go_to_bottom_right, when=obs_right_role_succeeded)
        node_go_to_bottom_right.connect_to(node_go_to_top_right, when=obs_right_role_succeeded)

    def current_tactic_succeed(self, i):
        return self.roles_graph[i].get_current_tactic().status_flag == Flags.SUCCESS

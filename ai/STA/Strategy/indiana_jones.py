# Under MIT License, see LICENSE.txt

from functools import partial

from Util.pose import Position, Pose
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags


class IndianaJones(Strategy):

    def __init__(self, game_state):
        super().__init__(game_state)

        indiana = self.assigned_roles[Role.MIDDLE]
        indiana_role = Role.MIDDLE
        obs_right = self.assigned_roles[Role.FIRST_DEFENCE]
        obs_right_role = Role.FIRST_DEFENCE
        obs_left = self.assigned_roles[Role.SECOND_DEFENCE]
        obs_left_role = Role.SECOND_DEFENCE

        # Positions objectifs d'Indiana Jones
        FIELD_GOAL_INTERNAL_X = self.game_state.field.our_goal_area.left
        goal_left  = (Pose(Position(+FIELD_GOAL_INTERNAL_X, 0), indiana.pose.orientation))
        goal_right = (Pose(Position(-FIELD_GOAL_INTERNAL_X, 0), indiana.pose.orientation))

        # Positions objectifs des obstacles
        y_bottom = self.game_state.field.bottom + 500
        y_top = self.game_state.field.top - 500
        x_left = self.game_state.field.left + 500
        x_right = self.game_state.field.right - 500

        node_go_to_goal_left = self.create_node(indiana_role, GoToPositionPathfinder(self.game_state, indiana, goal_left, cruise_speed=2))
        node_go_to_goal_right = self.create_node(indiana_role, GoToPositionPathfinder(self.game_state, indiana, goal_right, cruise_speed=2))

        indiana_succeeded = partial(self.current_tactic_succeed, indiana_role)

        node_go_to_goal_left.connect_to(node_go_to_goal_right, when=indiana_succeeded)
        node_go_to_goal_right.connect_to(node_go_to_goal_left, when=indiana_succeeded)

        node_go_to_top_left = self.create_node(obs_left_role, GoToPositionPathfinder(self.game_state, obs_left,
                                                            Pose(Position(x_left/2, y_top),
                                                                 obs_left.pose.orientation), cruise_speed=2))
        node_go_to_bottom_left = self.create_node(obs_left_role, GoToPositionPathfinder(self.game_state, obs_left,
                                                            Pose(Position(x_left/2, y_bottom), obs_left.pose.orientation)))
        obs_left_role_succeeded = partial(self.current_tactic_succeed, obs_left_role)

        node_go_to_top_left.connect_to(node_go_to_bottom_left, when=obs_left_role_succeeded)
        node_go_to_bottom_left.connect_to(node_go_to_top_left, when=obs_left_role_succeeded)

        node_go_to_top_right = self.create_node(obs_right_role, GoToPositionPathfinder(self.game_state,
                                                             obs_right, Pose(Position(x_right/2, y_top), obs_right.pose.orientation), cruise_speed=2))
        node_go_to_bottom_right = self.create_node(obs_right_role, GoToPositionPathfinder(self.game_state,
                                                             obs_right, Pose(Position(x_right/2, y_bottom), obs_right.pose.orientation), cruise_speed=2))
        obs_right_role_succeeded = partial(self.current_tactic_succeed, obs_right_role)

        node_go_to_top_right.connect_to(node_go_to_bottom_right, when=obs_right_role_succeeded)
        node_go_to_bottom_right.connect_to(node_go_to_top_right, when=obs_right_role_succeeded)

    def current_tactic_succeed(self, i):
        return self.roles_graph[i].current_tactic.status_flag == Flags.SUCCESS

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }
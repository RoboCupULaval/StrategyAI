# Under MIT license, see LICENSE.txt

from Util.pose import Pose, Position
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random

from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PreparePenaltyOffense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        our_goal = Pose(Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0), 0)

        role_to_positions = {Role.FIRST_ATTACK:   Pose.from_values(our_goal.position.x / 8, GameState().const["FIELD_Y_TOP"] * 2 / 3),
                             Role.SECOND_ATTACK:  Pose.from_values(our_goal.position.x / 8, GameState().const["FIELD_Y_TOP"] / 3),
                             Role.MIDDLE:         Pose.from_values(our_goal.position.x / 8, 0),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] / 3),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x / 8, GameState().const["FIELD_Y_BOTTOM"] * 2 / 3)}

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)
        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, our_goal, penalty_kick=True))

        for role, position in role_to_positions.items():
            player = self.assigned_roles[role]
            self.create_node(role, GoToPositionPathfinder(self.game_state, player, position))

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }

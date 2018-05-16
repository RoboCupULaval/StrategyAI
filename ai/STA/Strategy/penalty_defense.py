# Under MIT license, see LICENSE.txt
import numpy as np

from Util.pose import Pose, Position

from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PenaltyDefense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        their_goal = self.game_state.field.their_goal
        role_to_position = {Role.FIRST_ATTACK:   Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_TOP"] * 2 / 3),
                            Role.SECOND_ATTACK:  Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_TOP"] / 3),
                            Role.MIDDLE:         Pose.from_values(their_goal.x / 8, 0),
                            Role.FIRST_DEFENCE:  Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_BOTTOM"] / 3),
                            Role.SECOND_DEFENCE: Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_BOTTOM"] * 2 / 3)}

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper, penalty_kick=True))

        for role, position in role_to_position.items():
            position.orientation = np.pi
            self.create_node(role, GoToPositionPathfinder(self.game_state, self.assigned_roles[role], position))

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }


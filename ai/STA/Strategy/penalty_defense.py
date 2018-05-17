# Under MIT license, see LICENSE.txt

from Util.pose import Pose

from Util.role import Role
from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PenaltyDefense(TeamGoToPosition):
    def __init__(self, game_state):
        super().__init__(game_state)

        their_goal = game_state.field.their_goal
        role_to_positions = {Role.FIRST_ATTACK:   Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_TOP"] * 2 / 3),
                             Role.SECOND_ATTACK:  Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_TOP"] / 3),
                             Role.MIDDLE:         Pose.from_values(their_goal.x / 8, 0),
                             Role.FIRST_DEFENCE:  Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_BOTTOM"] / 3),
                             Role.SECOND_DEFENCE: Pose.from_values(their_goal.x / 8, GameState().const["FIELD_Y_BOTTOM"] * 2 / 3)}

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper, penalty_kick=True))

        self.assign_tactics(role_to_positions)

# Under MIT license, see LICENSE.txt

from Util.pose import Pose

from Util.role import Role
from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.penalty_goalkeeper import PenaltyGoalKeeper


class PenaltyDefense(TeamGoToPosition):
    def __init__(self, game_state):
        super().__init__(game_state)

        their_goal = game_state.field.their_goal
        role_to_positions = {Role.FIRST_ATTACK:   Pose.from_values(their_goal.x / 8, self.game_state.field.top * 2 / 3),
                             Role.SECOND_ATTACK:  Pose.from_values(their_goal.x / 8, self.game_state.field.top / 3),
                             Role.MIDDLE:         Pose.from_values(their_goal.x / 8, 0),
                             Role.FIRST_DEFENCE:  Pose.from_values(their_goal.x / 8, self.game_state.field.bottom / 3),
                             Role.SECOND_DEFENCE: Pose.from_values(their_goal.x / 8, self.game_state.field.bottom * 2 / 3)}

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, PenaltyGoalKeeper(game_state, goalkeeper))

        self.assign_tactics(role_to_positions)

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_ATTACK,
                Role.SECOND_ATTACK,
                Role.MIDDLE,
                Role.FIRST_DEFENCE,
                Role.SECOND_DEFENCE]

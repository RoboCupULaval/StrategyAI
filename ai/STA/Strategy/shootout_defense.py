# Under MIT license, see LICENSE.txt

from Util.pose import Pose

from Util.role import Role
from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.penalty_goalkeeper import PenaltyGoalKeeper


class ShootoutDefense(TeamGoToPosition):
    def __init__(self, game_state):
        super().__init__(game_state)
        field = self.game_state.field
        our_goal = field.our_goal_pose
        role_to_positions = {Role.SECOND_ATTACK: Pose.from_values(our_goal.position.x * 1 / 8, field.top * 4 / 5),
                             Role.MIDDLE: Pose.from_values(our_goal.position.x * 2 / 8, field.top * 4 / 5),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x * 4 / 8, field.top * 4 / 5),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x * 6 / 8, field.top * 4 / 5),
                             Role.FIRST_ATTACK:   Pose.from_values(our_goal.position.x * 7 / 8, field.top * 4 / 5)
                             }

        self.ball_start_position = self.game_state.ball_position

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        node_penalty_goalkeeper = self.create_node(Role.GOALKEEPER, PenaltyGoalKeeper(game_state, goalkeeper))
        node_goalkeeper = self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper))

        node_penalty_goalkeeper.connect_to(node_goalkeeper, when=self._ball_is_in_play)

        self.assign_tactics(role_to_positions)

    def _ball_is_in_play(self):
        return (self.game_state.ball_position - self.ball_start_position).norm > 50

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

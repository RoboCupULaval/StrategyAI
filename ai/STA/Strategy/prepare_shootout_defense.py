# Under MIT license, see LICENSE.txt

from Util.pose import Pose
from Util.role import Role

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.penalty_goalkeeper import PenaltyGoalKeeper
from ai.states.game_state import GameState


class PrepareShootoutDefense(TeamGoToPosition):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        field = self.game_state.field
        our_goal = field.our_goal_pose

        role_to_positions = {Role.SECOND_ATTACK: Pose.from_values(our_goal.position.x * 1 / 8, field.top * 4 / 5),
                             Role.MIDDLE: Pose.from_values(our_goal.position.x * 2 / 8, field.top * 4 / 5),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x * 4 / 8, field.top * 4 / 5),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x * 6 / 8, field.top * 4 / 5),
                             Role.FIRST_ATTACK:   Pose.from_values(our_goal.position.x * 7 / 8, field.top * 4 / 5)
                             }

        goalkeeper = self.game_state.get_player_by_role(Role.GOALKEEPER)
        self.create_node(Role.GOALKEEPER, PenaltyGoalKeeper(self.game_state, goalkeeper))

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
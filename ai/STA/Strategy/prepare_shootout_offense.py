# Under MIT license, see LICENSE.txt
import math

from Util.constant import ROBOT_RADIUS
from Util.pose import Pose
from Util.role import Role

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PrepareShootoutOffense(TeamGoToPosition):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        field = self.game_state.field
        our_goal = field.our_goal_pose
        shootout_x_position = field.their_goal_area.left + 6000 + 2 * ROBOT_RADIUS
        role_to_positions = {Role.GOALKEEPER:   Pose.from_values(our_goal.position.x * 1 / 8, field.top * 4 / 5),
                             Role.SECOND_ATTACK:  Pose.from_values(our_goal.position.x * 2 / 8, field.top * 4 / 5),
                             Role.MIDDLE:         Pose.from_values(shootout_x_position, 0),
                             Role.FIRST_DEFENCE:  Pose.from_values(our_goal.position.x * 4 / 8, field.top * 4 / 5),
                             Role.SECOND_DEFENCE: Pose.from_values(our_goal.position.x * 6 / 8, field.top * 4 / 5),
                             Role.FIRST_ATTACK: Pose.from_values(our_goal.position.x * 7 / 8, field.top * 4 / 5)
                             }

        self.assign_tactics(role_to_positions)

    @classmethod
    def required_roles(cls):
        return [Role.GOALKEEPER,
                Role.MIDDLE]

    @classmethod
    def optional_roles(cls):
        return [Role.FIRST_ATTACK,
                Role.SECOND_ATTACK,
                Role.FIRST_DEFENCE,
                Role.SECOND_DEFENCE]

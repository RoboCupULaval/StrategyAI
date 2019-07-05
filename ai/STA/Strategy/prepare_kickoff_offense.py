# Under MIT License, see LICENSE.txt
from math import pi

from Util.constant import ROBOT_RADIUS
from Util.pose import Pose
from Util.role import Role

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper


class PrepareKickOffOffense(TeamGoToPosition):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        # The two attackers must be ready for a pass
        # The top attack is a bit closer from the center, because the passing option hesitate between the two attackers
        attack_top_position = Pose.from_values(self.game_state.field.our_goal_x * 2 / 15,
                                               self.game_state.field.bottom * 4 / 5 - ROBOT_RADIUS,
                                               pi/2)
        attack_bottom_position = Pose.from_values(self.game_state.field.our_goal_x * 2 / 15,
                                                  self.game_state.field.top * 4 / 5,
                                                  -pi/2)
        middle_position = Pose.from_values(self.game_state.field.our_goal_x / 15, 0, 0)
        defense_top_position = Pose.from_values(self.game_state.field.our_goal_x / 2,
                                                self.game_state.field.top / 3, 0)
        defense_bottom_position = Pose.from_values(self.game_state.field.our_goal_x / 2,
                                                   self.game_state.field.bottom / 3, 0)

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper))

        role_to_positions = {Role.FIRST_ATTACK: attack_top_position,
                             Role.SECOND_ATTACK: attack_bottom_position,
                             Role.MIDDLE: middle_position,
                             Role.FIRST_DEFENCE: defense_top_position,
                             Role.SECOND_DEFENCE: defense_bottom_position}

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

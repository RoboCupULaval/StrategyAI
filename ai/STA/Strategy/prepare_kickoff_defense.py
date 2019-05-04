# Under MIT License, see LICENSE.txt
from Util.constant import REASONABLE_OFFSET, ROBOT_RADIUS
from Util.pose import Pose
from Util.role import Role
from ai.Algorithm.path_partitionner import Obstacle

from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PrepareKickOffDefense(TeamGoToPosition):

    def __init__(self, game_state):
        super().__init__(game_state)

        # Attribution des joueurs

        center_offset = game_state.field.center_circle_radius

        # Positions objectifs des joueurs
        attack_top_position = Pose.from_values(GameState().field.our_goal_x / 10,
                                               GameState().field.bottom * 3 / 5, 0)
        attack_bottom_position = Pose.from_values(GameState().field.our_goal_x / 10,
                                                  GameState().field.top * 3 / 5, 0)
        middle_position = Pose.from_values(center_offset + GameState().field.our_goal_x / 10, 0, 0)

        defense_top_position = Pose.from_values(GameState().field.our_goal_x / 2,
                                                GameState().field.top / 10, 0)
        defense_bottom_position = Pose.from_values(GameState().field.our_goal_x / 2,
                                                   GameState().field.bottom / 10, 0)

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(game_state, goalkeeper))

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


    def obstacles(self):
        min_distance = REASONABLE_OFFSET + ROBOT_RADIUS + self.game_state.field.center_circle_radius
        return [Obstacle(self.game_state.field.center.array, avoid_distance=min_distance)]
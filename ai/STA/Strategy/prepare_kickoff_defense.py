# Under MIT License, see LICENSE.txt

from Util.pose import Pose
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.team_go_to_position import TeamGoToPosition
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.states.game_state import GameState


class PrepareKickOffDefense(TeamGoToPosition):

    def __init__(self, game_state):
        super().__init__(game_state)

        # Attribution des joueurs

        center_offset = game_state.field.center_circle_radius

        # Positions objectifs des joueurs
        # FIXME: This is bad, the orientation of the player will always be the same,
        # independently of if we are in a positive or negative x
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
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.MIDDLE]
                }

    @classmethod
    def optional_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }
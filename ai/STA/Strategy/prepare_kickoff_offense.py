# Under MIT License, see LICENSE.txt
import numpy as np
from functools import partial

from Util.pose import Pose
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.goalkeeper import GoalKeeper
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class PrepareKickOffOffense(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        # Positions objectifs des joueurs
        attack_top_position = Pose.from_values(GameState().field.our_goal_x / 15,
                                   GameState().field.bottom * 3 / 5, 0)
        attack_bottom_position = Pose.from_values(GameState().field.our_goal_x / 15,
                                      GameState().field.top * 3 / 5, 0)
        middle_position = Pose.from_values(GameState().field.our_goal_x / 15, 0, 0)
        defense_top_position = Pose.from_values(GameState().field.our_goal_x / 2,
                                    GameState().field.top / 3, 0)
        defense_bottom_position = Pose.from_values(GameState().field.our_goal_x / 2,
                                       GameState().field.bottom / 3, 0)

        goalkeeper = self.assigned_roles[Role.GOALKEEPER]
        self.create_node(Role.GOALKEEPER, GoalKeeper(self.game_state, goalkeeper))

        role_to_positions = {Role.FIRST_ATTACK: attack_top_position,
                             Role.SECOND_ATTACK: attack_bottom_position,
                             Role.MIDDLE: middle_position,
                             Role.FIRST_DEFENCE: defense_top_position,
                             Role.SECOND_DEFENCE: defense_bottom_position}

        for role, position in role_to_positions.items():
            position.orientation = np.pi
            player = self.assigned_roles[role]
            node_go_to_position = self.create_node(role, GoToPositionPathfinder(self.game_state, player, position))
            node_stop = self.create_node(role, Stop(self.game_state, player))
            player_arrived_to_position = partial(self.arrived_to_position, player)
            node_go_to_position.connect_to(node_stop, when=player_arrived_to_position)

    @classmethod
    def required_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in [Role.GOALKEEPER,
                                                                Role.FIRST_ATTACK,
                                                                Role.SECOND_ATTACK,
                                                                Role.MIDDLE,
                                                                Role.FIRST_DEFENCE,
                                                                Role.SECOND_DEFENCE]
                }

    def arrived_to_position(self, player):
        role = GameState().get_role_by_player_id(player.id)
        return self.roles_graph[role].current_tactic.status_flag == Flags.SUCCESS

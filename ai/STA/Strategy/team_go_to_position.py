# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class TeamGoToPosition(Strategy):
    def __init__(self, game_state):
        super().__init__(game_state)

    def assign_tactics(self, role_to_positions):
        for role, position in role_to_positions.items():
            position.orientation = np.pi
            player = self.assigned_roles[role]
            node_go_to_position = self.create_node(role, GoToPosition(self.game_state, player, position))
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

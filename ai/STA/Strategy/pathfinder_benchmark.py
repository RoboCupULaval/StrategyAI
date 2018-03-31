# Under MIT license, see LICENSE.txt
from Util.position import Position
from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.Algorithm.Graph.Graph import Graph
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_random_pose_in_zone import GoToRandomPosition


class PathfinderBenchmark(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        for role, player in self.assigned_roles.items():
            self.create_node(role, GoToRandomPosition(self.game_state, player, Position(-1400, 900), 1800, 2700))

    @classmethod
    def required_roles(cls):
        return {}

    @classmethod
    def optional_roles(cls):
        return {r: keep_prev_mapping_otherwise_random for r in Role}


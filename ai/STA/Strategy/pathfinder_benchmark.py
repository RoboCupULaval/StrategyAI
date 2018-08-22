# Under MIT license, see LICENSE.txt
from Util.position import Position
from Util.role import Role

from ai.Algorithm.Graph.Graph import Graph
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_random_pose_in_zone import GoToRandomPosition


class PathfinderBenchmark(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        for role, player in self.assigned_roles.items():
            self.create_node(role, GoToRandomPosition(self.game_state, player,
                                                      center_of_zone=Position(-0, 0),
                                                      width_of_zone=2000,
                                                      height_of_zone=2000))

    @classmethod
    def required_roles(cls):
        return []

    @classmethod
    def optional_roles(cls):
        return [r for r in Role]


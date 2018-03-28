# Under MIT license, see LICENSE.txt
from Util.position import Position
from Util.role import Role
from ai.Algorithm.Graph.Graph import Graph
from ai.STA.Strategy.strategy import Strategy
from ai.STA.Tactic.go_to_random_pose_in_zone import GoToRandomPosition


class PathfinderBenchmark(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.roles_graph = {r: Graph() for r in Role.as_list()}
        role_mapping = {Role.GOALKEEPER: 4, Role.MIDDLE: 6}
        self.game_state.map_players_to_roles_by_player_id(role_mapping)

        roles_to_consider = Role.as_list()

        role_by_robots = [(i, self.game_state.get_player_by_role(i)) for i in roles_to_consider if self.game_state.get_player_by_role(i) is not None]

        for index, player in role_by_robots:
            self.create_node(index, GoToRandomPosition(self.game_state, player, Position(-1400, 900), 1800, 2700))

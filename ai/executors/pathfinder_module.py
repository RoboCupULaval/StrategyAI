
import logging
from collections import defaultdict
from typing import Dict
from ai.Algorithm.path_partitionner import PathPartitionner

MIN_DISTANCE_FROM_OBSTACLE = 250


class PathfinderModule:
    def __init__(self):
        self.paths = defaultdict(lambda: None)
        self.logger = logging.getLogger("PathfinderModule")
        self.pathfinder = PathPartitionner(avoid_radius=MIN_DISTANCE_FROM_OBSTACLE)
        self.obstacles = []

    def exec(self, game_state, ai_cmds) -> Dict:

        self.updates_obstacles(game_state)

        for player, ai_cmd in ai_cmds.items():
            if ai_cmd.pathfinder_on and ai_cmd.target:
                player_obstacles = self.player_obstacles(game_state, player, ai_cmd)
                self.paths[player] = self.pathfinder.get_path(start=player.pose.position,
                                                              target=ai_cmd.target.position,
                                                              obstacles=player_obstacles,
                                                              last_path=self.paths[player])
            else:
                self.paths[player] = None

        return self.paths

    def updates_obstacles(self, game_state):

        self.obstacles.clear()

        our_team = [player for player in game_state.our_team.available_players.values()]
        enemy_team = [player for player in game_state.enemy_team.available_players.values()]

        for other in our_team + enemy_team:
            self.obstacles.append(other.pose.position)

    def player_obstacles(self, game_state, player, ai_cmd):
        path_obstacles = self.obstacles.copy()

        if ai_cmd.ball_collision and game_state.is_ball_on_field:
            path_obstacles.append(game_state.ball_position)

        path_obstacles.remove(player.pose.position)

        return path_obstacles

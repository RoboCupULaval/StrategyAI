
import logging
from collections import defaultdict
from queue import Queue
from typing import Dict, List

from Util import AICommand, Position
from ai.Algorithm.path_partitionner import PathPartitionner, Obstacle
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState

MIN_DISTANCE_FROM_OBSTACLE = 200


class WayPoint:
    def __init__(self, position: Position, ball_collision: bool = True):
        self.position = position
        self.ball_collision = ball_collision


class PathfinderModule:
    def __init__(self, ui_send_queue: Queue):
        self.ui_send_queue = ui_send_queue
        self.paths = defaultdict(lambda: None)
        self.sub_paths = defaultdict(lambda: [None])
        self.logger = logging.getLogger("PathfinderModule")
        self.pathfinder = PathPartitionner(self.ui_send_queue)
        self.obstacles = []
        self.strategy_obstacles = []
        self.game_state = GameState()

    def exec(self, ai_cmds: Dict[Player, AICommand], strategy_obstacles) -> Dict:

        self.updates_obstacles()
        self.strategy_obstacles = strategy_obstacles
        for player, ai_cmd in ai_cmds.items():
            if ai_cmd.target is not None:
                self.paths[player] = self.generate_path(player, ai_cmd)
            else:
                self.paths[player] = None

        return self.paths

    def updates_obstacles(self):

        self.obstacles.clear()

        our_team = [player for player in self.game_state.our_team.available_players.values()]
        enemy_team = [player for player in self.game_state.enemy_team.available_players.values()]

        for other in our_team + enemy_team:
            self.obstacles.append(Obstacle(position=other.position.array,
                                           velocity=other.velocity.position.array,
                                           avoid_distance=MIN_DISTANCE_FROM_OBSTACLE))

    def player_optional_obstacles(self, ball_collision: bool) -> List[Obstacle]:
        path_obstacles = self.obstacles.copy()

        if ball_collision and self.game_state.is_ball_on_field:
            path_obstacles.append(Obstacle(position=self.game_state.ball_position.array,
                                           velocity=self.game_state.ball_velocity.array,
                                           avoid_distance=MIN_DISTANCE_FROM_OBSTACLE))

        return path_obstacles

    def generate_path(self, player, ai_cmd: AICommand):
        way_points = ai_cmd.way_points
        start = player.position
        target = ai_cmd.target.position
        path_to_target = self.sub_paths[player][-1]
        sub_paths = []

        if len(way_points) > 0:

            if len(way_points) == (len(self.sub_paths[player])-1):
                last_paths = self.sub_paths[player][:-1]
            else:
                last_paths = [None for _ in way_points]

            way_point = way_points[0]
            path_temp = self.generate_simple_path(start, way_point, player, last_paths[0])
            path = path_temp
            sub_paths += [path_temp]
            start = way_point.position

            if len(way_points) > 1:
                for way_point, last_path in zip(way_points[1:], last_paths[1:]):
                    sub_paths += [self.generate_simple_path(start, way_point, player, last_path)]
                    start = way_point.position

            # path reliant le dernier way_point à la target
            path_temp = self.generate_simple_path(way_points[-1].position,
                                                  WayPoint(target, ai_cmd.ball_collision), player,
                                                  path_to_target)
            path += path_temp
            sub_paths += [path_temp]
        else:
            path = self.generate_simple_path(start, WayPoint(target, ai_cmd.ball_collision), player, path_to_target)
            sub_paths += [path]
        self.sub_paths[player] = sub_paths
        path.filter(threshold=10)
        return path

    def generate_simple_path(self, start: Position, way_point: WayPoint, player: Player, last_path=None):

        player_obstacles = self.obstacles.copy()
        player_obstacles += self.strategy_obstacles
        player_obstacles += self.player_optional_obstacles(way_point.ball_collision)

        path = PathPartitionner(self.ui_send_queue).get_path(start=start,
                                                              target=way_point.position,
                                                             obstacles=player_obstacles,
                                                             player=player,
                                                             last_path=last_path)
        return path


def remove_ball_collision(obstacles):
    return [obs for obs in obstacles if obs.object_type is None]

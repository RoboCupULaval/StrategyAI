
import logging
from collections import defaultdict
from typing import Dict, List

from Util import AICommand, Position, Path
from ai.Algorithm.path_partitionner import PathPartitionner, Obstacle
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState

MIN_DISTANCE_FROM_OBSTACLE = 200


class WayPoint:
    def __init__(self, position: Position, ball_collision: bool = True):
        self.position = position
        self.ball_collision = ball_collision

    def __repr__(self) -> str:
        return 'WayPoint' + str(self.position)


class PathfinderModule:
    def __init__(self):
        self.paths = defaultdict(lambda: None)
        self.sub_paths = defaultdict(lambda: [None])
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pathfinder = PathPartitionner()
        self.obstacles = []
        self.strategy_obstacles = []
        self.game_state = GameState()

    def exec(self, ai_cmds: Dict[Player, AICommand], strategy_obstacles) -> Dict:

        self.updates_obstacles()
        self.strategy_obstacles = strategy_obstacles
        for player, ai_cmd in ai_cmds.items():
            if ai_cmd.target is not None:
                if ai_cmd.enable_pathfinder:
                    self.paths[player] = self.generate_path(player, ai_cmd)
                else:
                    self.paths[player] = Path(start=player.position, target=ai_cmd.target.position)
            else:
                self.paths[player] = None

        return self.paths

    def updates_obstacles(self):

        self.obstacles.clear()

        our_team = [player for player in self.game_state.our_team.available_players.values()]
        enemy_team = [player for player in self.game_state.enemy_team.available_players.values()]

        for other in our_team:
            self.obstacles.append(Obstacle(other.position.array, avoid_distance=MIN_DISTANCE_FROM_OBSTACLE))

        for other in enemy_team:
            avoid_distance = MIN_DISTANCE_FROM_OBSTACLE
            if other.position in self.game_state.field.their_goal_forbidden_area:
                avoid_distance *= 2
            self.obstacles.append(Obstacle(other.position.array, avoid_distance=avoid_distance))

    def player_optional_obstacles(self, ball_collision: bool) -> List[Obstacle]:
        path_obstacles = self.obstacles.copy()

        if ball_collision and self.game_state.is_ball_on_field:
            path_obstacles.append(Obstacle(self.game_state.ball_position.array,
                                           avoid_distance=150))

        return path_obstacles

    def generate_path(self, player, ai_cmd: AICommand):

        way_points = ai_cmd.way_points
        start = player.position
        target = ai_cmd.target.position
        sub_paths = []
        path_positions = [WayPoint(start, ball_collision=ai_cmd.ball_collision), *way_points,
                          WayPoint(target, ball_collision=ai_cmd.ball_collision)]
        for i in range(len(path_positions)-1):
            sub_paths.append(self.generate_simple_path(path_positions[i].position, path_positions[i+1],
                                                       player.velocity.position))
        path = sub_paths[0]
        for i in range(len(sub_paths)-1):
            path += sub_paths[i+1]

        path.filter(threshold=10)
        return path

    def generate_simple_path(self, start: Position, way_point: WayPoint, velocity: Position, last_path=None):

        player_obstacles = self.obstacles.copy()
        player_obstacles += self.strategy_obstacles
        player_obstacles += self.player_optional_obstacles(way_point.ball_collision)

        path = PathPartitionner().get_path(start=start,
                                           target=way_point.position,
                                           obstacles=player_obstacles,
                                           player_velocity=velocity,
                                           last_path=last_path)
        return path


def remove_ball_collision(obstacles):
    return [obs for obs in obstacles if obs.object_type is None]

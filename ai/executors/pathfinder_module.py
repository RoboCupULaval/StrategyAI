
import logging
from collections import defaultdict
from typing import Dict, List

from Util import AICommand, Position
from ai.Algorithm.path_partitionner import PathPartitionner, Obstacle
from ai.GameDomainObjects import Player
from ai.states.game_state import GameState

MIN_DISTANCE_FROM_OBSTACLE = 250


class PathfinderModule:
    def __init__(self):
        self.paths = defaultdict(lambda: None)
        self.logger = logging.getLogger("PathfinderModule")
        self.pathfinder = PathPartitionner()
        self.obstacles = []

    def exec(self, game_state: GameState, ai_cmds: Dict[Player, AICommand]) -> Dict:

        self.updates_obstacles(game_state)

        for player, ai_cmd in ai_cmds.items():
            if ai_cmd.target is not None:
                player_obstacles = self.player_optionnal_obstacles(game_state, ai_cmd)
                self.paths[player] = self.pathfinder.get_path(start=player.position,
                                                              target=ai_cmd.target.position,
                                                              obstacles=player_obstacles,
                                                              last_path=self.paths[player])
            else:
                self.paths[player] = None

        return self.paths

    def updates_obstacles(self, game_state: GameState):

        self.obstacles.clear()

        our_team = [player for player in game_state.our_team.available_players.values()]
        enemy_team = [player for player in game_state.enemy_team.available_players.values()]

        for other in our_team + enemy_team:
            self.obstacles.append(Obstacle(other.position.array, avoid_distance=MIN_DISTANCE_FROM_OBSTACLE))


    def player_optionnal_obstacles(self, game_state: GameState, ai_cmd: AICommand) -> List[Obstacle]:
        path_obstacles = self.obstacles.copy()

        if ai_cmd.ball_collision and game_state.is_ball_on_field:
            path_obstacles.append(Obstacle(game_state.ball_position.array, avoid_distance=MIN_DISTANCE_FROM_OBSTACLE))

        if ai_cmd.ball_collision and game_state.is_ball_on_field:
            path_obstacles.append(Obstacle(game_state.ball_position.array, avoid_distance=MIN_DISTANCE_FROM_OBSTACLE))
        path_obstacles.append(Obstacle(Position(-game_state.field.our_goal[0], game_state.field.goal_width / 2).array,
                                       avoid_distance=game_state.field.goal_width))
        path_obstacles.append(Obstacle(Position(-game_state.field.our_goal[0], -(game_state.field.goal_width) / 2).array,
                                       avoid_distance=game_state.field.goal_width))
        path_obstacles.append(Obstacle(Position(game_state.field.their_goal[0], game_state.field.goal_width / 2).array,
                                       avoid_distance=game_state.field.goal_width))
        path_obstacles.append(Obstacle(Position(game_state.field.their_goal[0], -(game_state.field.goal_width) / 2).array,
                                       avoid_distance=game_state.field.goal_width))

        return path_obstacles

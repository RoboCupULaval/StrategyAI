import time
from typing import List

from RULEngine.Debug.debug_interface import COLOR_ID_MAP, DEFAULT_PATH_TIMEOUT
from RULEngine.Util.Position import Position
from ai.Algorithm.PathfinderRRT import PathfinderRRT
from ai.Algorithm.path_partitionner import PathPartitionner, Path, CollisionBody
from ai.Util.ai_command import AICommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService
import concurrent.futures
from multiprocessing import Pool
from functools import partial
import numpy as np
from profilehooks import profile

INTERMEDIATE_DISTANCE_THRESHOLD = 540
AIcommands = List[AICommand]


def create_pathfinder(game_state, type_of_pathfinder):
    assert isinstance(type_of_pathfinder, str)
    assert type_of_pathfinder.lower() in ["path_part"]

    if type_of_pathfinder.lower() == "path_part":
        return PathPartitionner(game_state)
    else:
        raise TypeError("Couldn't init a pathfinder with the type of ",
                        type_of_pathfinder, "!")


def pathfind_ai_commands(type_pathfinder, game_state, player) -> Path:
    last_path = None
    last_raw_path = None
    field = game_state.game.field
    if player.ai_command is None or not player.ai_command.pathfinder_on:
        return None
    if player.pathfinder_history.last_pose_goal is not None:
        MIN_CHANGE_IN_GOAL = 200
        if (player.pathfinder_history.last_pose_goal - player.ai_command.pose_goal.position).norm() < MIN_CHANGE_IN_GOAL:
            last_path = player.pathfinder_history.last_path
            last_raw_path = player.pathfinder_history.last_raw_path
    pathfinder = create_pathfinder(game_state, type_pathfinder)
    if type_pathfinder == "path_part":
        player.ai_command.pose_goal.position = \
            field.respect_field_rules(Position(player.ai_command.pose_goal.position[0],
                                               player.ai_command.pose_goal.position[1]))
        optionnal_collision_bodies = field.field_collision_body
        collision_bodies = get_pertinent_collision_objects(player, game_state, optionnal_collision_bodies)
        path, raw_path = pathfinder.get_path(player,
                                             player.ai_command.pose_goal,
                                             player.ai_command.cruise_speed,
                                             last_path,
                                             last_raw_path,
                                             end_speed=player.ai_command.end_speed,
                                             ball_collision=player.ai_command.collision_ball,
                                             optional_collision=collision_body)
        MIN_CHANGE_FOR_RECALCULATE = 100
        if path.get_path_length() < MIN_CHANGE_FOR_RECALCULATE:
            player.pathfinder_history.last_path = None
            player.pathfinder_history.last_pose_goal = path.goal
        else:
            player.pathfinder_history.last_path = path
            player.pathfinder_history.last_pose_goal = path.goal
        player.pathfinder_history.last_raw_path = raw_path

        player.ai_command.path = path.points[1:]
        player.ai_command.path_speeds = path.speeds
        player.ai_command.path_turn = path.turns
        return path

    else:
        path = pathfinder.get_path(player,
                                   player.ai_command.pose_goal,
                                   player.ai_command.cruise_speed)
        player.ai_command.path = path
        # print(time.time() - start)
        return path


def get_pertinent_collision_objects(commanded_player, game_state, optionnal_collision_bodies=None):
    factor = 1.1
    collision_bodies = []
    # FIXME: Find better name that is less confusing between self.player and player
    for player in game_state.my_team.available_players.values():
        if player.id != commanded_player.id:
            if (commanded_player.pose.position - player.pose.position).norm() + \
                    (commanded_player.ai_command.pose_goal.position - player.pose.position).norm() < \
                    (commanded_player.ai_command.pose_goal.position - commanded_player.pose.position).norm() * factor:
                collision_bodies.append(
                    CollisionBody(player.pose.position, player.velocity.position, commanded_player.gap_proxy))
    for player in game_state.other_team.available_players.values():
        if (commanded_player.pose.position - player.pose.position).norm() + \
                    (commanded_player.ai_command.pose_goal.position - player.pose.position).norm() < \
                    (commanded_player.ai_command.pose_goal.position - commanded_player.pose.position).norm() * factor:
            collision_bodies.append(
                CollisionBody(player.pose.position, player.velocity.position, commanded_player.gap_proxy))
    if optionnal_collision_bodies is None:

        return collision_bodies
    else:
        return collision_bodies + optionnal_collision_bodies

class PathfinderModule(Executor):

    def __init__(self, world_state: WorldState):
        super().__init__(world_state)
        self.type_of_pathfinder = ConfigService().config_dict["STRATEGY"]["pathfinder"]
        self.last_time_pathfinding_for_robot = {}
        self.last_frame = time.time()
        self.game_state = world_state.game_state

    def exec(self):

        callback = partial(pathfind_ai_commands, self.type_of_pathfinder.lower(), self.game_state)
        paths = [callback(player) for player in list(self.ws.game_state.my_team.available_players.values())]

        for path in paths:
            if path is not None:
                self.draw_path(path)

    def draw_path(self, path, pid=0):

        points = []
        for idx, path_element in enumerate(path.points):
            x = path_element.x
            y = path_element.y
            points.append((x, y))
            if self.type_of_pathfinder.lower() == "path_part":
                if idx == 0:
                    pass
                else:
                    self.ws.debug_interface.add_line(points[idx - 1], points[idx], timeout=0.1)

        #    print(points)
        #self.ws.debug_interface.add_multi_line(points)
        self.ws.debug_interface.add_multiple_points(points[1:], COLOR_ID_MAP[pid], width=5, link="path - " + str(pid),
                                                    timeout=DEFAULT_PATH_TIMEOUT)

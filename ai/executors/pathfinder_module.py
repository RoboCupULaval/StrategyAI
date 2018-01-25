import time
from functools import partial
from typing import List

from Util.ai_command_shit import AICommand
from Util import Position
from ai.Algorithm.path_partitionner import PathPartitionner, Path
from ai.states.game_state import GameState
from config.config_service import ConfigService

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
        collision_body = field.field_collision_body
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
        return path

    else:
        path = pathfinder.get_path(player,
                                   player.ai_command.pose_goal,
                                   player.ai_command.cruise_speed)
        player.ai_command.path = path
        # print(time.time() - start)
        return path

class PathfinderModule:

    def __init__(self):
        super().__init__()
        self.type_of_pathfinder = ConfigService().config_dict["STRATEGY"]["pathfinder"]
        self.last_time_pathfinding_for_robot = {}
        self.last_frame = time.time()
        self.game_state = GameState()

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

        #    print(points)
        # self.ws.debug_interface.add_multi_line(points)

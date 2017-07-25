import time
from typing import List

from RULEngine.Debug.debug_interface import COLOR_ID_MAP, DEFAULT_PATH_TIMEOUT
from ai.Algorithm.PathfinderRRT import PathfinderRRT
from ai.Algorithm.path_partitionner import PathPartitionner, Path
from ai.Util.ai_command import AICommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService
import concurrent.futures
from multiprocessing import Pool
from functools import partial
from profilehooks import profile

INTERMEDIATE_DISTANCE_THRESHOLD = 540
AIcommands = List[AICommand]


def create_pathfinder(game_state, type_of_pathfinder):
    assert isinstance(type_of_pathfinder, str)
    assert type_of_pathfinder.lower() in ["rrt", "astar", "path_part"]

    if type_of_pathfinder.lower() == "rrt":
        return PathfinderRRT(game_state)
    elif type_of_pathfinder.lower() == "path_part":
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
        if (player.pathfinder_history.last_pose_goal - player.ai_command.pose_goal.position).norm() < 200:
            # player.pathfinder_history.last_pose_goal = player.ai_command.pose_goal.position
            last_path = player.pathfinder_history.last_path
            last_raw_path = player.pathfinder_history.last_raw_path
    pathfinder = create_pathfinder(game_state, type_pathfinder)
    if type_pathfinder == "path_part":
        player.ai_command.pose_goal.position = field.respect_field_rules(player.ai_command.pose_goal.position)
        collision_body = field.field_collision_body
        path, raw_path = pathfinder.get_path(player,
                                             player.ai_command.pose_goal,
                                             player.ai_command.cruise_speed,
                                             last_path,
                                             last_raw_path,
                                             end_speed=player.ai_command.end_speed,
                                             ball_collision=player.ai_command.collision_ball,
                                             optional_collision=collision_body)

        if path.get_path_length() < 100:
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

class PathfinderModule(Executor):

    def __init__(self, world_state: WorldState):
        super().__init__(world_state)
        self.type_of_pathfinder = ConfigService().config_dict["STRATEGY"]["pathfinder"]
        self.last_time_pathfinding_for_robot = {}
        self.last_frame = time.time()
        self.game_state = world_state.game_state
        # self.last_path = None
        # self.last_raw_path = None
        # self.last_pose_goal = None
        #self.pool = Pool(processes=12)

    #@profile(immediate=True)
    def exec(self):
        callback = partial(pathfind_ai_commands, self.type_of_pathfinder.lower(), self.game_state)
        paths = [callback(player) for player in list(self.ws.game_state.my_team.available_players.values())]
        #print(len(self.ws.game_state.my_team.available_players.values()))
        #paths = self.pool.map(callback, self.game_state.my_team.available_players.values())
        for path in paths:
            if path is not None:
                self.draw_path(path)


    # TODO find what this does? MGL 2017/05/17
    """
    def _modify_path_for_cinematic_constraints(self, ai_commandes: list):
        for cmd in ai_commandes:
            target = self._find_intermediate_target(cmd.robot_id, cmd.path)
            self.ws.debug_interface.add_log(3, "Target feed in CinePath: {}".format(target))
            cmd.path = self.cinematic_pathfinder.get_path(cmd.robot_id, target)

    def _find_intermediate_target(self, robot_id, path):
        default_target = path[0]
        player_pst = self.ws.game_state.get_player_pose(robot_id).position
        for target in path:
            if get_distance(player_pst, target) > INTERMEDIATE_DISTANCE_THRESHOLD:
                return target
        return default_target
    """

    def change_pathfinder(self, type_of_pathfinder):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar", "path_part"]

        self.pathfinder = self.get_pathfinder(type_of_pathfinder)

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

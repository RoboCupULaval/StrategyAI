import time

from RULEngine.Debug.debug_interface import COLOR_ID_MAP, DEFAULT_PATH_TIMEOUT
from RULEngine.Util.geometry import get_distance
from ai.Algorithm.AsPathManager import AsPathManager
from ai.Algorithm.CinePath.CinePath import CinePath
from ai.Algorithm.PathfinderRRT import PathfinderRRT
from ai.Algorithm.path_partitionner import PathPartitionner
from ai.Util.ai_command import AICommand
from ai.executors.executor import Executor
from ai.states.world_state import WorldState
from config.config_service import ConfigService
from typing import List

INTERMEDIATE_DISTANCE_THRESHOLD = 540
AIcommands = List[AICommand]

class PathfinderModule(Executor):

    def __init__(self, p_world_state: WorldState):
        super().__init__(p_world_state)
        self.type_of_pathfinder = ConfigService().config_dict["STRATEGY"]["pathfinder"]
        self.pathfinder = self.get_pathfinder(self.type_of_pathfinder)
        self.last_time_pathfinding_for_robot = {}
        self.last_frame = time.time()
        self.cinematic_pathfinder = CinePath(p_world_state)
        self.last_path = None
        self.last_raw_path = None

    def exec(self):
        ai_commands = self._get_aicommand_that_need_path()
        self._adjust_from_last_time_of_exec(ai_commands)
        self._pathfind_ai_commands(ai_commands)
        #self._modify_path_for_cinematic_constraints(ai_commands)

    def _get_aicommand_that_need_path(self):
        aicommands_list = self.ws.play_state.current_ai_commands
        aic_with_pathfinding_on = []

        for ai_c in aicommands_list.values():
            if ai_c.pathfinder_on:
                aic_with_pathfinding_on.append(ai_c)

        return aic_with_pathfinding_on

    def _adjust_from_last_time_of_exec(self, ai_commands_to_adjust):
        pass
        if time.time() - self.last_frame > 10:
            self.last_frame = time.time()
            ai_commands_to_adjust.clear()

    def _pathfind_ai_commands(self, ai_commands:AIcommands):
        for ai_c in ai_commands:

            #self.time = time.time()

            # print(self.time - time.time())
            if self.type_of_pathfinder.lower() == "path_part":
                path, raw_path = self.pathfinder.get_path(ai_c.robot_id, ai_c.pose_goal,
                                                          ai_c.cruise_speed, self.last_path, self.last_raw_path)
                self.draw_path(path)
                #self.draw_path(raw_path, 1)
                self.last_path = path
                self.last_raw_path = raw_path
                ai_c.path = path.points[1:]
                ai_c.path_speeds = path.speeds
            else:
                path = self.pathfinder.get_path(ai_c.robot_id, ai_c.pose_goal)
                ai_c.path = path

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

    def change_pathfinder(self, type_of_pathfinder):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar", "path_part"]

        self.pathfinder = self.get_pathfinder(type_of_pathfinder)

    def get_pathfinder(self, type_of_pathfinder):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar", "path_part"]

        if type_of_pathfinder.lower() == "astar":
            return AsPathManager(self.ws, ConfigService().config_dict["GAME"]["type"] == "sim")
        elif type_of_pathfinder.lower() == "rrt":
            return PathfinderRRT(self.ws)
        elif type_of_pathfinder.lower() == "path_part":
            return PathPartitionner(self.ws)
        else:
            raise TypeError("Couldn't init a pathfinder with the type of ",
                            type_of_pathfinder, "!")

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
                    self.ws.debug_interface.add_line(points[idx - 1], points[idx])

        #    print(points)
        self.ws.debug_interface.add_multiple_points(points[1:], COLOR_ID_MAP[pid], width=5, link="path - " + str(pid),
                                                    timeout=DEFAULT_PATH_TIMEOUT)

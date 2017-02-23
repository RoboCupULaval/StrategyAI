import time

from RULEngine.Debug.debug_interface import DebugInterface, COLOR_ID_MAP, DEFAULT_PATH_TIMEOUT
from ai.Algorithm.AsPathManager import AsPathManager
from ai.Algorithm.PathfinderRRT import PathfinderRRT
from ai.executors.executor import Executor


class PathfinderModule(Executor):

    def __init__(self, p_world_state, type_of_pathfinder, is_simulation):
        super().__init__(p_world_state)
        self.debug_interface = DebugInterface()
        self.pathfinder = self.get_pathfinder(type_of_pathfinder, is_simulation)
        self.last_time_pathfinding_for_robot = {}
        self.last_frame = time.time()

    def exec(self):
        ai_commands = self._get_aicommand_that_need_path()
        self._adjust_from_last_time_of_exec(ai_commands)
        self._pathfind_ai_commands(ai_commands)
        # self._return_new_ai_commands(ai_commands)

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

    def _pathfind_ai_commands(self, ai_commands):
        for ai_c in ai_commands:
            path = self.pathfinder.get_path(ai_c.robot_id, ai_c.pose_goal)
            self.draw_path(path)
            ai_c.path = path

    def change_pathfinder(self, type_of_pathfinder):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar"]

        self.pathfinder = self.get_pathfinder(type_of_pathfinder)

    def get_pathfinder(self, type_of_pathfinder, is_simulation):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar"]

        if type_of_pathfinder.lower() == "astar":
            # place pathfinder here
            return AsPathManager(self.ws)  # is_simulation)
        elif type_of_pathfinder.lower() == "rrt":
            # place pathfinder here
            return PathfinderRRT(self.ws)
        else:
            raise TypeError("Couldn't init a pathfinder with the type of ",
                            type_of_pathfinder, "!")

    def draw_path(self, path, pid=0):
        points = []
        for path_element in path:
            x = path_element.x
            y = path_element.y
            points.append((x, y))
        self.debug_interface.add_multiple_points(points, COLOR_ID_MAP[pid], width=5, link="path - " + str(pid),
                                                 timeout=DEFAULT_PATH_TIMEOUT)

from ai.executors.executor import Executor
from ai.Algorithm.PathfinderRRT import PathfinderRRT


class PathfinderModule(Executor):

    def __init__(self, p_world_state, type_of_pathfinder):
        super().__init__(p_world_state)

        self.pathfinder = self.get_pathfinder(type_of_pathfinder)
        self.last_time_pfding_for_robot = {}

    def exec(self):
        ai_commands = self._get_aicommand_that_need_path()
        self._adjust_from_last_time_of_exec(ai_commands)
        self._pathfind_ai_commands(ai_commands)
        self._return_new_ai_commands(ai_commands)

    def _get_aicommand_that_need_path(self):
        aicommands_list = self.ws.play_state.current_ai_commands
        path_on_aic = []

        for ai_c in aicommands_list.values():
            if ai_c.pathfinder_on:
                path_on_aic.append(ai_c)

        return path_on_aic

    def _adjust_from_last_time_of_exec(self, ai_commands_to_adjust):
        # don't do it since we did it last frame or something like that
        for ai_c in ai_commands_to_adjust:
            pass

    def _pathfind_ai_commands(self, ai_commands):
        for ai_c in ai_commands:
            self.pathfinder.get_path(ai_c.robot_id, ai_c.pose_goal)

    def _return_new_ai_commands(self, ai_commands):
        pass

    def change_pathfinder(self, type_of_pathfinder):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar"]

        self.pathfinder = self.get_pathfinder(type_of_pathfinder)

    def get_pathfinder(self, type_of_pathfinder):
        assert isinstance(type_of_pathfinder, str)
        assert type_of_pathfinder.lower() in ["rrt", "astar"]

        if type_of_pathfinder.lower() == "astar":
            # place pathfinder here
            return None
        elif type_of_pathfinder.lower() == "rrt":
            # place pathfinder here
            return PathfinderRRT(self.ws)
        else:
            raise TypeError("Couldn't init a pathfinder with the type of ",
                            type_of_pathfinder, "!")

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
        # self._return_new_ai_commands(ai_commands)

    def _get_aicommand_that_need_path(self):
        aicommands_list = self.ws.play_state.current_ai_commands
        aic_with_pathfinding_on = []

        for ai_c in aicommands_list.values():
            if ai_c.pathfinder_on:
                aic_with_pathfinding_on.append(ai_c)

        return aic_with_pathfinding_on

    def _adjust_from_last_time_of_exec(self, ai_commands_to_adjust):
        # don't do it since we did it last frame or something like that
        # TODO
        pass

    def _pathfind_ai_commands(self, ai_commands):
        for ai_c in ai_commands:
            path = self.pathfinder.get_path(ai_c.robot_id, ai_c.pose_goal)
            ai_c.path = path

    """
    def _return_new_ai_commands(self, ai_commands):
        current_ai_c = self.ws.play_state.current_ai_commands
        for ai_c in ai_commands:
            if current_ai_c.get(ai_c.robot_id, 0):
                current_ai_c[ai_c.robot_id] = ai_c
    """

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

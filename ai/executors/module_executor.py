# Under MIT License, see LICENSE.txt

from ai.executors.executor import Executor
from ai.Algorithm.PathfinderRRT import PathfinderRRT


class ModuleExecutor(Executor):

    def __init__(self, p_world_state):
        super().__init__(p_world_state)
        self.pathfinder = None

        self.start_initial_modules()

    def exec(self):
        for module in self.ws.module_state.modules.values():

            module.update()



    def start_initial_modules(self):
        self.ws.module_state.pathfinder = PathfinderRRT(self.ws)

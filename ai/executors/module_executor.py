# Under MIT License, see LICENSE.txt

from ai.executors.executor import Executor
from ai.executors.pathfinder_module import PathfinderModule


class ModuleExecutor(Executor):

    def __init__(self, p_world_state, type_of_pathfinder):
        super().__init__(p_world_state)

        self.start_initial_modules(type_of_pathfinder)

    def exec(self):
        for module in self.ws.module_state.modules.values():

            module.update()
        self.ws.module_state.pathfinder_module.exec()

    def start_initial_modules(self, type_of_pathfinder):
        self.ws.module_state.pathfinder_module = \
            PathfinderModule(self.ws, type_of_pathfinder)

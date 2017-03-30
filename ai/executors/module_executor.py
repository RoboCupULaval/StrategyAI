# Under MIT License, see LICENSE.txt

from ai.executors.executor import Executor
from ai.executors.pathfinder_module import PathfinderModule
from ai.states.world_state import WorldState


class ModuleExecutor(Executor):

    def __init__(self, p_world_state: WorldState, type_of_pathfinder: str, is_simulation: bool):
        super().__init__(p_world_state)
        self.is_simulation = is_simulation
        self.start_initial_modules(type_of_pathfinder)

    def exec(self) -> None:
        """
        Update les modules intelligents et execute le module du pathfinder

        :return: None
        """
        for module in self.ws.module_state.modules.values():
            module.update()
        self.ws.module_state.pathfinder_module.exec()

    def start_initial_modules(self, type_of_pathfinder: str) -> None:
        """
        Initialise les modules intelligents et le pathdfinder.

        :param type_of_pathfinder: (str) le nom du pathfinder à utiliser
        :return: None
        """
        self.ws.module_state.pathfinder_module = \
            PathfinderModule(self.ws, type_of_pathfinder, self.is_simulation)

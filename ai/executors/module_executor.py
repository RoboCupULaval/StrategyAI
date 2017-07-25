# Under MIT License, see LICENSE.txt

from ai.executors.executor import Executor
from ai.executors.pathfinder_module import PathfinderModule
from ai.states.world_state import WorldState
import threading
import time

class ModuleExecutor(Executor):

    def __init__(self, world_state: WorldState):
        super().__init__(world_state)
        self.start_initial_modules()
        self.t1 = None
        self.t2 = None
    def exec(self) -> None:
        """
        Update les modules intelligents et execute le module du pathfinder

        :return: None
        """
        self.t1 = threading.Thread(target=self.exec_pathfinder_module)
        self.t2 = threading.Thread(target=self.exec_display_player_kalman)
        self.t3 = threading.Thread(target=self.exec_display_ball_kalman)
        for module in self.ws.module_state.modules.values():
            module.update()
        self.t1.start()
        self.t2.start()
        self.t3.start()
        self.t1.join()
        self.t2.join()
        self.t3.join()
    def start_initial_modules(self) -> None:
        """
        Initialise les modules intelligents et le pathfinder.

        :return: None
        """
        self.ws.module_state.pathfinder_module = PathfinderModule(self.ws)

    def exec_pathfinder_module(self):
        return self.ws.module_state.pathfinder_module.exec()

    def exec_display_player_kalman(self):
        return self.ws.game_state.display_player_kalman()

    def exec_display_ball_kalman(self):
        return self.ws.game_state.display_ball_kalman()
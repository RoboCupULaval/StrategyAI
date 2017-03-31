# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.game_world import GameWorld
from ai.executors.regulator import PositionRegulator
from ai.states.world_state import WorldState
from ai.executors.debug_executor import DebugExecutor
from ai.executors.module_executor import ModuleExecutor
from ai.executors.play_executor import PlayExecutor
from ai.executors.command_executor import CommandExecutor
from ai.executors.movement_executor import MovementExecutor


class Coach(object):

    def __init__(self, mode_debug_active=True, pathfinder="path_part", is_simulation=True):
        """
        Initialise le coach de l'IA.

        :param mode_debug_active: (bool) indique si les commandes de debug sont actives
        :param pathfinder:  (str) indique le nom du pathfinder par défault
        :param is_simulation:   (bool) indique si en simulation (true) ou en vrai vie (false)
        """
        self.mode_debug_active = mode_debug_active
        self.is_simulation = is_simulation

        # init the states
        self.world_state = WorldState()

        # init the executors
        self.debug_executor = DebugExecutor(self.world_state)
        self.play_executor = PlayExecutor(self.world_state)
        self.module_executor = ModuleExecutor(self.world_state, pathfinder, is_simulation)
        self.movement_executor = MovementExecutor(self.world_state)
        self.regulator_executor = PositionRegulator(self.world_state, is_simulation)
        self.robot_command_executor = CommandExecutor(self.world_state)

        # logging
        DebugInterface().add_log(1, "\nCoach initialized with \nmode_debug_active = "+str(mode_debug_active) +
                                 "\npathfinder = "+str(pathfinder)+"\nis_simulation = "+str(is_simulation))

    def main_loop(self) -> List:
        """
        Execute un tour de boucle de l'IA

        :return: List(_Command) les commandes des robots
        """
        # main loop de l'IA
        self.debug_executor.exec()
        self.play_executor.exec()
        self.module_executor.exec()
        self.movement_executor.exec()
        self.regulator_executor.exec()
        robot_commands = self.robot_command_executor.exec()

        return robot_commands

    def set_reference(self, world_reference: GameWorld) -> None:
        """
        Permet de mettre les références dans le worldstate et le debugexecutor.

        :param world_reference: Objet GameWorld contenant les références des objets en jeu provenant du RULEngine.
                                C'est un data transfert object.
        :return: None.
        """
        self.world_state.set_reference(world_reference)
        self.debug_executor.set_reference(world_reference.debug_info)

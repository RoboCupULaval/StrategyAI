# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.reference_transfer_object import ReferenceTransferObject
from ai.states.world_state import WorldState
from ai.executors.debug_executor import DebugExecutor
from ai.executors.module_executor import ModuleExecutor
from ai.executors.play_executor import PlayExecutor
from ai.executors.command_executor import CommandExecutor
from ai.executors.motion_executor import MotionExecutor
from config.config_service import ConfigService
import time

class Coach(object):

    def __init__(self):
        """
        Initialise le coach de l'IA.

        :param mode_debug_active: (bool) indique si les commandes de debug sont actives
        :param pathfinder:  (str) indique le nom du pathfinder par défault
        :param is_simulation:   (bool) indique si en simulation (true) ou en vrai vie (false)
        """
        cfg = ConfigService()
        self.mode_debug_active = cfg.config_dict["DEBUG"]["using_debug"] == "true"
        self.is_simulation = cfg.config_dict["GAME"]["type"] == "sim"

        # init the states
        self.world_state = WorldState()

        # init the executors
        self.debug_executor = DebugExecutor(self.world_state)
        self.play_executor = PlayExecutor(self.world_state)
        self.module_executor = ModuleExecutor(self.world_state)
        self.motion_executor = MotionExecutor(self.world_state)
        self.robot_command_executor = CommandExecutor(self.world_state)


        # logging
        DebugInterface().add_log(1, "\nCoach initialized with \nmode_debug_active = "+str(self.mode_debug_active) +
                                 "\nis_simulation = "+str(self.is_simulation))

    def main_loop(self) -> List:
        """
        Execute un tour de boucle de l'IA

        :return: List(_Command) les commandes des robots
        """
        # main loop de l'IA
        # debug code! no remove pls (au moins pas avant le Japon)
        print([i.id for i in self.world_state.game_state.my_team.available_players.values()])
        start_debug_interface = time.time()
        self.debug_executor.exec()
        end_debug_interface = time.time()
        start_play_executor = time.time()
        self.play_executor.exec()
        end_play_executor = time.time()
        start_module_executor = time.time()
        self.module_executor.exec()
        end_module_executor = time.time()
        start_motion_executor = time.time()
        self.motion_executor.exec()
        end_motion_executor = time.time()
        start_robot_commands = time.time()
        robot_commands = self.robot_command_executor.exec()
        end_robot_commands = time.time()

        somme = end_debug_interface - start_debug_interface + end_play_executor - start_debug_interface + \
                end_module_executor - start_module_executor + end_motion_executor - start_motion_executor + \
                end_robot_commands - start_robot_commands

        # print("debug_interface:",  end_debug_interface - start_debug_interface)
        # print("play_executor:", end_play_executor - start_debug_interface)
        # print("module_executor:", end_module_executor - start_module_executor)
        # print("motion_executor:", end_motion_executor - start_motion_executor)
        # print("robot_commands:", end_robot_commands - start_robot_commands)
        # print("somme:", somme)
        return robot_commands

    def set_reference(self, world_reference: ReferenceTransferObject) -> None:
        """
        Permet de mettre les références dans le worldstate et le debugexecutor.

        :param world_reference: Objet GameWorld contenant les références des objets en jeu provenant du RULEngine.
                                C'est un data transfert object.
        :return: None.
        """
        self.world_state.set_reference(world_reference)
        self.debug_executor.set_reference(world_reference.debug_info)

# Under MIT License, see LICENSE.txt
from typing import List

from RULEngine.Debug.debug_interface import DebugInterface
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
        Celui-ci s'occupe d'appeler tout les morceaux de l'ia dans le bon ordre pour prendre une décision de jeu
        """
        # todo seee the validity of this MGL 2017/10/28
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
        # debug code! no remostart_play_executorve pls (au moins pas avant le Japon)

        start_debug_interface = time.time()
        self.debug_executor.exec()
        end_debug_interface = start_play_executor = time.time()
        self.play_executor.exec()
        end_play_executor = start_module_executor = time.time()
        self.module_executor.exec()
        end_module_executor = start_motion_executor = time.time()
        self.motion_executor.exec()
        end_motion_executor = start_robot_commands = time.time()
        robot_commands = self.robot_command_executor.exec()
        end_robot_commands = time.time()

        dt_debug = end_debug_interface - start_debug_interface
        dt_play_exe = end_play_executor - start_play_executor
        dt_module_exe = end_module_executor - start_module_executor
        dt_motion_exe = end_motion_executor - start_motion_executor
        dt_robot_cmd = end_robot_commands - start_robot_commands
        sum = dt_debug + dt_play_exe + dt_module_exe + dt_motion_exe + dt_robot_cmd

        # Profiling code for debuging, DO NOT REMOVE
        #print("[{:4.1f}ms total] debug_inter:{:4.1f}ms/{:4.1f}% | play_exec:{:4.1f}ms/{:4.1f}% | module_exec:{:4.1f}ms/{:4.1f}% | motion_exec:{:4.1f}ms/{:4.1f}% | robot_cmd:{:4.1f}ms/{:3.1f}%"
        #      .format(sum*1000,
        #              dt_debug*1000, dt_debug/sum*100.0,
        #              dt_play_exe*1000, dt_play_exe/sum*100.0,
        #              dt_module_exe*1000, dt_module_exe/sum*100.0,
        #              dt_motion_exe*1000, dt_motion_exe/sum*100.0,
        #              dt_robot_cmd*1000, dt_robot_cmd/sum*100.0))

        return robot_commands

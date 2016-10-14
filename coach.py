# Under MIT License, see LICENSE.txt

from ai.states.WorldState import WorldState
from ai.executors.DebugExecutor import DebugExecutor
from ai.executors.ModuleExecutor import ModuleExecutor
from ai.executors.PlayExecutor import PlayExecutor
from ai.executors.RobotCommandExecutor import RobotCommandExecutor

# FIXME this thing!
TIMESTAMP_MINIMAL_DELTA = 0.015


class Coach(object):

    def __init__(self, is_team_yellow, mode_debug_active=True):
        self.mode_debug_active = mode_debug_active
        # For the framework! TODO make this better!
        self.debug_commands = []
        self.robot_commands = []

        self.world_state = WorldState(is_team_yellow)
        self.debug_executor = DebugExecutor(self.world_state)
        self.module_executor = ModuleExecutor(self.world_state)
        self.play_executor = PlayExecutor(self.world_state)
        self.robot_command_executor = RobotCommandExecutor(self.world_state)

    def main_loop(self, p_game_state):
        self.robot_commands.clear()
        self.debug_commands.clear()

        self.world_state.update(p_game_state)

        self.debug_executor.exec()
        self.module_executor.exec()
        self.play_executor.exec()
        self.robot_command_executor.exec()
        self.debug_executor.exec()

        self.robot_commands = self.world_state.play_state.ready_to_ship_robot_packet_list
        if self.mode_debug_active:
            self.debug_commands = self.world_state.debug_state.to_ui_packet_debug_cmds

    def get_robot_commands(self):
        return self.robot_commands

    def get_debug_status(self):
        return self.mode_debug_active

    # FIXME only the debug command are accessed through method, the robot_commands are take straight from the variable!
    def get_debug_commands_and_clear(self):
        return self.debug_commands

    # Throwback for the last coach! TODO see if we still need to implement them! Or HOW!
    def halt(self):
        """ Hack pour sync les frames de vision et les itérations de l'IA """
        pass

    def stop(self, game_state):
        """ *Devrait* déinit pour permettre un arrêt propre. """
        pass

# Under MIT License, see LICENSE.txt
from RULEngine.Debug.debug_interface import DebugInterface
from ai.executors.regulator import PositionRegulator
from ai.states.world_state import WorldState
from ai.executors.debug_executor import DebugExecutor
from ai.executors.module_executor import ModuleExecutor
from ai.executors.play_executor import PlayExecutor
from ai.executors.command_executor import CommandExecutor
from ai.executors.movement_executor import MovementExecutor
# FIXME this thing!
TIMESTAMP_MINIMAL_DELTA_60_FPS = 0.017
TIMESTAMP_MINIMAL_DELTA_30_FPS = 0.033


class Coach(object):

    def __init__(self, mode_debug_active=True, pathfinder="astar", is_simulation=True):
        self.mode_debug_active = mode_debug_active
        self.is_simulation = is_simulation
        # For the framework! TODO make this better!
        self.debug_commands = []
        self.robot_commands = []

        self.world_state = WorldState()
        self.debug_executor = DebugExecutor(self.world_state)
        self.module_executor = ModuleExecutor(self.world_state, pathfinder, is_simulation)
        self.play_executor = PlayExecutor(self.world_state)
        self.movement_executor = MovementExecutor(self.world_state)
        self.regulator_executor = PositionRegulator(self.world_state, is_simulation)
        self.robot_command_executor = CommandExecutor(self.world_state)
        DebugInterface().add_log(1, "\nCoach initialized with \nmode_debug_active = "+str(mode_debug_active) +
                                 "\npathfinder = "+str(pathfinder)+"\nis_simulation = "+str(is_simulation))

    def main_loop(self):
        self.robot_commands.clear()
        self.debug_commands.clear()

        self.debug_executor.exec()
        self.play_executor.exec()
        self.module_executor.exec()
        self.movement_executor.exec()
        self.regulator_executor.exec()
        self.robot_commands = self.robot_command_executor.exec()

        return self.robot_commands

    def set_reference(self, world_reference):
        self.world_state.set_reference(world_reference)
        self.debug_executor.set_reference(world_reference.debug_info)


    # not used see if we can delete.
    def get_debug_status(self):
        return self.mode_debug_active

    # Throwback for the last coach! TODO see if we still need to implement
    # them! Or HOW!
    def halt(self):
        """ Hack pour sync les frames de vision et les itérations de l'IA """
        pass

    def stop(self, game_state):
        """ *Devrait* déinit pour permettre un arrêt propre. """
        pass

from ai.states.WorldState import WorldState
from ai.executors.DebugExecutor import DebugExecutor


TIMESTAMP_MINIMAL_DELTA = 0.015


class Coach(object):

    def __init__(self, mode_debug_active=True):
        self.mode_debug_active = mode_debug_active
        # For the framework! TODO make this better!
        self.debug_commands = []
        self.robot_commands = []

        self.world_state = WorldState()
        self.debug_executor = DebugExecutor()

    def main_loop(self, p_game_state):
        self.robot_commands.clear()
        self.debug_commands.clear()

        self.world_state.update(p_game_state)

    def get_robot_commands(self):
        return self.robot_commands

    def get_debug_status(self):
        return self.mode_debug_active

    # FIXME only the debug command are accessed through method, the robot_commands are take straight from the variable!
    def get_debug_commands_and_clear(self):
        return self.debug_commands

    # Throwback for the last coach! TODO see if we still need to implement them!
    def halt(self):
        """ Hack pour sync les frames de vision et les itérations de l'IA """
        pass

    def stop(self, game_state):
        """ *Devrait* déinit pour permettre un arrêt propre. """
        pass

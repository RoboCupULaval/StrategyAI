from ai.managers import ModuleManager, GameStateManager, DebugManager, PlayManager, RobotCommandManager


TIMESTAMP_MINIMAL_DELTA = 0.015


class Coach(object):

    def __init__(self, mode_debug_active=True):

        self.managers = {}
        self.mode_debug_active = mode_debug_active

        # GameStateManager initialisation
        self.GameStateManager = GameStateManager.GameStateManager()
        self.managers["GameStateManager"] = self.GameStateManager

        # Intelligent module manager intialisation
        self.ModuleManager = ModuleManager.ModuleManager(self.GameStateManager)
        self.managers["ModuleManager"] = self.ModuleManager

        # PlayManager initialisation
        self.PlayManager = PlayManager.PlayManager(self.GameStateManager)
        self.managers["PlayManager"] = self.PlayManager

        # debug subprocess initialisation
        if mode_debug_active:
            self.DebugManager = DebugManager.DebugManager(self.GameStateManager, self.PlayManager)
            self.managers["Debug"] = self.DebugManager
            self.PlayManager.register_debug_manager(self.DebugManager)

        # The sender of command! ...doesn't send anything - shhhhh!
        self.RobotCommandManager = RobotCommandManager.RobotCommandManager(self.GameStateManager,
                                                                           self.DebugManager,
                                                                           self.PlayManager)
        self.managers[RobotCommandManager] = self.RobotCommandManager

        # For the framework! TODO make this better!
        self.debug_commands = []
        self.robot_commands = []

    def main_loop(self, p_game_state):
        self.robot_commands.clear()
        self.debug_commands.clear()

        self.GameStateManager.update(p_game_state)

        self.debug_commands = self.DebugManager.update()
        self.ModuleManager.update()
        self.PlayManager.update()
        self.RobotCommandManager.update()
        self.robot_commands = self.RobotCommandManager.get_robots_commands()

    def get_robot_commands(self):
        return self.robot_commands

    def get_debug_status(self):
        return self.mode_debug_active

    def acquire_manager(self, module_name):
        return self.managers[module_name]

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

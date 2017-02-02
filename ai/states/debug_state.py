# Under MIT License, see LICENSE.txt

from ai.Util.singleton import Singleton


class DebugState(object, metaclass=Singleton):

    def __init__(self):
        self.from_ui_debug_commands = None
        self.transformed_ui_debug_commands = []

        self.from_ai_raw_debug_cmds = []
        self.to_ui_packet_debug_cmds = []

    def update(self):
        self.transformed_ui_debug_commands.clear()
        self.from_ai_raw_debug_cmds.clear()
        self.to_ui_packet_debug_cmds.clear()

    def set_reference(self, world_reference):
        self.from_ui_debug_commands = world_reference.debug_info

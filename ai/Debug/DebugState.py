

class DebugState:

    def __init__(self):
        self.from_ui_debug_commands = None
        self.transformed_ui_debug_commands = []

        self.from_ai_raw_debug_cmds = []
        self.to_ui_packet_debug_cmds = []

    def update(self, incoming_debug_information):
        self.from_ui_debug_commands = None
        self.transformed_ui_debug_commands.clear()
        self.from_ai_raw_debug_cmds.clear()
        self.to_ui_packet_debug_cmds.clear()

        self.from_ui_debug_commands = incoming_debug_information

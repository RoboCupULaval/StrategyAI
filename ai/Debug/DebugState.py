

class DebugState:

    def __init__(self):
        self.raw_ui_debug_commands = None
        self.transformed_ui_debug_commands = []
        self.to_ui_debug_commands = []

    def update(self, incoming_debug_information):
        self.raw_ui_debug_commands = None
        self.transformed_ui_debug_commands.clear()
        self.to_ui_debug_commands.clear()

        self.raw_ui_debug_commands = incoming_debug_information

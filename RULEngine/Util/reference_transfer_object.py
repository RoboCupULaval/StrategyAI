

class ReferenceTransferObject:

    def __init__(self, p_game):
        self.game = p_game
        self.debug_info = None
        self.timestamp = 0
        self.team_color_svc = None

    def set_timestamp(self, timestamp_ref)->None:
        self.timestamp = timestamp_ref

    def set_team_color_svc(self, p_team_color_svc)->None:
        self.team_color_svc = p_team_color_svc

    def set_debug(self, debug_ref)->None:
        self.debug_info = debug_ref

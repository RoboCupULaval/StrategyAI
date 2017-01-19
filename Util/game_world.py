

class GameWorld:

    def __init__(self, p_game):
        self.game = p_game
        self.debug_info = []
        self.timestamp = None
        self.team_color_svc = None

    def set_team_color_svc(self, p_team_color_svc):
        self.team_color_svc = p_team_color_svc

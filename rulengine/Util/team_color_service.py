from RULEngine.Util.constant import TeamColor


class TeamColorService:
    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = self.__init__(*args, **kwargs)
        return self._instances[self]

    def __init__(self, team_color):

        if team_color == TeamColor.YELLOW_TEAM:
            self.OUR_TEAM_COLOR = TeamColor.YELLOW_TEAM
            self.ENEMY_TEAM_COLOR = TeamColor.BLUE_TEAM
        elif team_color == TeamColor.BLUE_TEAM:
            self.OUR_TEAM_COLOR = TeamColor.BLUE_TEAM
            self.ENEMY_TEAM_COLOR = TeamColor.YELLOW_TEAM
        else:
            raise Exception("Couleur non defini")

from RULEngine.Util.constant import TeamColor


class TeamColorService:
    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = self.__init__(*args, **kwargs)
        return self._instances[self]

    def __init__(self, are_we_team_yellow):

        if are_we_team_yellow:
            self.OUR_TEAM_COLOR = TeamColor.YELLOW_TEAM
            self.ENEMY_TEAM_COLOR = TeamColor.BLUE_TEAM
        else:
            self.OUR_TEAM_COLOR = TeamColor.BLUE_TEAM
            self.ENEMY_TEAM_COLOR = TeamColor.YELLOW_TEAM

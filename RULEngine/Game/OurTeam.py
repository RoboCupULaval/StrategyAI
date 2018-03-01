from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Game.Team import Team
from RULEngine.Util.constant import TeamColor, PLAYER_PER_TEAM
from config.config_service import ConfigService


class OurTeam(Team):

    def __init__(self, team_color: TeamColor):
        super().__init__(team_color)
        # It is our team so we use our player!
        for player_id in range(PLAYER_PER_TEAM):
            self.players[player_id] = OurPlayer(self, player_id)
            if (ConfigService().config_dict["GAME"]["type"] == "sim" and 0 <= player_id <= 5)\
                    or (ConfigService().config_dict["GAME"]["type"] == "real" and 1 <= player_id <= 6):
                self.available_players[player_id] = self.players[player_id]

    # todo change this MGL 2017/05/29
    def update_player_command(self, player_id, cmd):
        try:
            self.players[player_id].set_command(cmd)
        except KeyError as err:
            raise err

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Game.Team import Team
from RULEngine.Util.constant import TeamColor, PLAYER_PER_TEAM


class OurTeam(Team):

    def __init__(self, team_color: TeamColor):
        super().__init__(team_color)
        # It is our team so we use our player!
        self.available_players = {}
        for player_id in range(PLAYER_PER_TEAM):
            self.players[player_id] = OurPlayer(self, player_id)
            if player_id < 6:
                self.players[player_id].in_play = True
                self.available_players[player_id] = self.players[player_id]

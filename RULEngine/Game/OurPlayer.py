from RULEngine.Game.Player import Player
from RULEngine.Util.team_color_service import TeamColorService


class OurPlayer(Player):
    kalman_type = 'friend'

    def __init__(self):
        tcs = TeamColorService()
        super().__init__(team=tcs)
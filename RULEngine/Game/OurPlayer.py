from RULEngine.Game.Player import Player
from RULEngine.Util.kalman_filter.friend_kalman_filter import FriendKalmanFilter


class OurPlayer(Player):

    def __init__(self, team, id):
        super().__init__(team=team, id=id)

        self.kf = FriendKalmanFilter()
        self.ai_command = None


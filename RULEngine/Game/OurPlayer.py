from RULEngine.Game.Player import Player
from RULEngine.Util.kalman_filter.friend_kalman_filter import FriendKalmanFilter


class OurPlayer(Player):
    max_speed = 2
    max_angular_speed = 6.2
    max_acc = 1

    def __init__(self, team, id):
        super().__init__(team=team, id=id)

        self.kf = FriendKalmanFilter()
        self.ai_command = None
        self.pid = None  # for the moment
        self.in_play = False


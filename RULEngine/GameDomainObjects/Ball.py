# Under MIT License, see LICENSE.txt
from RULEngine.Util.kalman_filter.ball_kalman_filter import BallKalmanFilter
from ..Util.Position import Position


class Ball:
    kalman_type = 'ball'

    def __init__(self):
        self.position = Position()
        self.velocity = Position()

    def update(self, poses, delta):
        pass
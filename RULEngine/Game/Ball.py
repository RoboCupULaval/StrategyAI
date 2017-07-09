# Under MIT License, see LICENSE.txt
from RULEngine.Util.kalman_filter.ball_kalman_filter import BallKalmanFilter
from ..Util.Position import Position


class Ball:
    kalman_type = 'ball'

    def __init__(self):
        self.position = Position()
        self.velocity = Position()
        self.kf = BallKalmanFilter()

    def kalman_update(self, poses, delta):
        # print(poses)
        ret = self.kf.filter(poses, delta)
        self.position = Position(ret[0], ret[1])
        self.velocity = Position(ret[2], ret[3])

    def set_position(self, pos, delta):
        if pos != self.position and delta != 0:
            self.velocity.x = (pos.x - self.position.x) / delta
            self.velocity.y = (pos.y - self.position.y) / delta
            # FIXME: hack
            # print(math.sqrt(self.velocity.x**2 + self.velocity.y**2))
            # print(delta)

            self.position = pos

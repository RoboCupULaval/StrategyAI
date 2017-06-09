from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.kalman_filter.friend_kalman_filter import FriendKalmanFilter
from ai.Util.pathfinder_history import PathfinderHistory


class OurPlayer(Player):
    max_speed = 2
    max_angular_speed = 6.2
    max_acc = 0.8

    def __init__(self, team, id: int):
        super().__init__(team=team, id=id)

        self.kf = FriendKalmanFilter()
        self.ai_command = None
        self.pid = None  # for the moment
        self.in_play = False
        self.update = self._friend_kalman_update
        self.pathfinder_history = PathfinderHistory()

    def _friend_kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, self.cmd, delta)
        self.pose = Pose(Position(ret[0], ret[1]), ret[4])
        self.velocity = [ret[2], ret[3], ret[5]]

    def set_command(self, cmd):
        self.cmd = [cmd.cmd_repr.position.x, cmd.cmd_repr.position.y, cmd.cmd_repr.orientation]


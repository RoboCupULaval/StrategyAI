from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.SpeedPose import SpeedPose
from RULEngine.Util.Position import Position
from RULEngine.Util.kalman_filter.friend_kalman_filter import FriendKalmanFilter
from ai.Util.pathfinder_history import PathfinderHistory


class OurPlayer(Player):
    max_speed = 3
    max_angular_speed = 3.14
    max_acc = 2
    max_angular_acc = 0.3

    def __init__(self, team, id: int):
        super().__init__(team=team, id=id)
        self.cmd = None
        self.kf = FriendKalmanFilter()
        self.ai_command = None
        self.pid = None  # for the moment
        self.in_play = False
        self.update = self._friend_kalman_update
        self.pathfinder_history = PathfinderHistory()
        self.collision_body_mask = [0, 0]
        self.receiver_pass_flag = False


    def _friend_kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, self.cmd, delta)
        self.pose = Pose(Position(ret[0], ret[1]), ret[4])
        self.velocity = SpeedPose(Position(ret[2], ret[3]), ret[5])

    def set_command(self):
        if self.ai_command.speed is not None:
            self.cmd = [self.ai_command.speed.position.x,
                        self.ai_command.speed.position.y,
                        self.ai_command.speed.orientation]
        else:
            self.cmd = None

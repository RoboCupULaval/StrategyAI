# Under MIT License, see LICENSE.txt
from RULEngine.Util.kalman_filter.enemy_kalman_filter import EnemyKalmanFilter
from config.config_service import ConfigService
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position


class Player:

    def __init__(self, team, id):
        self.cmd = None
        self.id = id
        self.team = team
        self.pose = Pose()
        self.velocity = Pose()
        self.kf = EnemyKalmanFilter()
        self.update = self._update
        if ConfigService().config_dict["IMAGE"]["kalman"] == "true":
            self.update = self._kalman_update

    def has_id(self, pid):
        return self.id == pid

    def _update(self, pose):
        self.pose = pose

    def _kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, delta)
        self.pose = Pose(Position(ret[0], ret[1]), ret[4])
        self.velocity = Pose(Position(ret[2], ret[3]), ret[5])

    def check_if_on_field(self):
        return self.pose == Pose()

    def __str__(self):
        return str(self.team.team_color.name)+" "+str(self.id)+"   "

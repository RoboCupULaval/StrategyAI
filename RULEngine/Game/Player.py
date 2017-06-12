# Under MIT License, see LICENSE.txt
import RULEngine.Util.Position
from RULEngine.Util.kalman_filter.enemy_kalman_filter import EnemyKalmanFilter
from config.config_service import ConfigService
from ..Util.Pose import Pose
from ..Util.constant import DELTA_T


class Player:

    def __init__(self, team, id):

        self.cmd = [0, 0, 0]

        self.id = id
        self.team = team
        self.pose = Pose()
        self.velocity = [0, 0, 0]
        self.kf = EnemyKalmanFilter()
        self.update = self._update
        if ConfigService().config_dict["IMAGE"]["kalman"] == "true":
            self.update = self._kalman_update

    def has_id(self, pid):
        return self.id == pid

    def _update(self, pose, delta=DELTA_T):
        old_pose = self.pose
        self.pose = pose

    def _kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, delta)
        self.pose = Pose(RULEngine.Util.Position.Position(ret[0], ret[1]), ret[4])
        self.velocity = [ret[2], ret[3], ret[5]]

    def __str__(self):
        return str(self.team.team_color.name)+" id: "+str(self.id)+"   "+str(hex(id(self)))
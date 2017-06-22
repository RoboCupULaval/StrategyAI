# Under MIT License, see LICENSE.txt
import RULEngine.Util.Position
from RULEngine.Util.kalman_filter.enemy_kalman_filter import EnemyKalmanFilter
from config.config_service import ConfigService
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position


class Player:

    def __init__(self, team, id):
        self.cmd = [0, 0, 0]
        self.id = id
        self.team = team
        self.pose = Pose()
        self.velocity = Pose()
        self.kf = EnemyKalmanFilter()
        self.update = self._update
        if ConfigService().config_dict["IMAGE"]["kalman"] == "true":
            self.update = self._enemy_kalman_update

    def has_id(self, pid):
        return self.id == pid

    def _update(self, pose):
        self.pose = pose

    def _enemy_kalman_update(self, poses, delta):
        ret = self.kf.filter(poses, delta)
        self.pose = Pose(Position(ret[0], ret[1]), ret[4])
        self.velocity = Pose(Position(ret[2], ret[3]), ret[5])

    def __str__(self):
        return str(self.team.team_color.name)+" id: "+str(self.id)+"   "+str(hex(id(self)))

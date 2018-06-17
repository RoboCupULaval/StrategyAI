# Under MIT License, see LICENSE.txt

from Util.pose import Pose
from config.config import Config


class Player:

    def __init__(self, number_id: int, team):
        assert isinstance(number_id, int)
        assert number_id in range(0, Config()['ENGINE']['max_robot_id'])

        self._id = number_id
        self._team = team
        self._pose = Pose()
        self._velocity = Pose()

    def update(self, new_pose: Pose, new_velocity: Pose):
        self.pose = new_pose
        self.velocity = new_velocity

    def has_id(self, pid):
        return self.id == pid

    def __str__(self):
        return '{} {}'.format(self.team.team_color.name, self.id)

    @property
    def id(self):
        return self._id

    @property
    def team(self):
        return self._team

    @property
    def position(self):
        return self._pose.position

    @property
    def pose(self):
        return self._pose

    @property
    def orientation(self):
        return self._pose.orientation

    @pose.setter
    def pose(self, value: Pose):
        assert isinstance(value, Pose)
        self._pose = value

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value: Pose):
        assert isinstance(value, Pose)
        self._velocity = value

    @property
    def team_color(self):
        return self.team.team_color

# Under MIT License, see LICENSE.txt
from RULEngine.GameDomainObjects.team import Team
from RULEngine.Util.Pose import Pose


class Player:

    def __init__(self, number_id: int, team: Team):
        assert isinstance(number_id, int)
        assert number_id in [x for x in range(1, 13)]

        self._id = number_id
        self._team = team
        self._pose = Pose()
        self._velocity = Pose()

    def has_id(self, pid):
        return self.id == pid

    def __str__(self):
        return str(self.team.team_color.name)+" "+str(self.id)

    @property
    def id(self):
        return self._id

    @property
    def team(self):
        return self._team

    @property
    def pose(self):
        return self._pose

    @pose.setter
    def pose(self, value):
        assert isinstance(value, Pose)
        self._pose = value

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        assert isinstance(value, Pose)
        self._velocity = value

    @property
    def team_color(self):
        return self.team.team_color

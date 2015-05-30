__author__ = 'mathieu'
import math

from PythonFramework.Command import Command
from PythonFramework.Strategy.Strategy import Strategy
from PythonFramework.Util.Position import Position
from PythonFramework.Util.Pose import Pose
import time


class TestStrategy(Strategy):
    def __init__(self, field, referee, team, opponent_team):
        super().__init__(field, referee, team, opponent_team)

    def on_start(self):
        """
        A way to send a command to your robots
        """
        for player in self.team.players:
            command = Command.Rotate(player, self.team, 90)
            self._send_command(command)

    def on_halt(self):
        """
        A way to instantiate pose and positions : dont forget to import Util!
        """
        aPose = Pose(Position(10, 20), 90)  # define a pose with x = 10, y = 20, z = 0, theta = 90
        aPosition = Position(10, 20, 30)  # define a position with x = 10, y = 20, z = 30


    def on_stop(self):
        """
        A way to retrieve player positions and ball.
        """
        aPlayer = self.team.players[0]
        aPlayerFromTheOtherTeam = self.opponent_team.players[0]
        print("Player pose : ", aPlayer.pose)
        print("Player id : ", aPlayer.id)
        print("Player2 pose : ", aPlayerFromTheOtherTeam.pose)
        print("Player2 id : ", aPlayerFromTheOtherTeam.id)
        theBall = self.field.ball
        print("Ball Position : ", theBall.position)


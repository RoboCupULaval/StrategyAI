# Under MIT License, see LICENSE.txt

from functools import partial
from random import shuffle

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.DemoFollowBall import DemoFollowBall
from ai.STA.Tactic.DemoFollowRobot import DemoFollowRobot
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.Joystick import Joystick


class BambaFollow(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robot1 = self.game_state.my_team.available_players[4]
        robot2 = self.game_state.my_team.available_players[2]
        robot3 = self.game_state.my_team.available_players[3]
        self.add_tactic(robot1.id, DemoFollowBall(self.game_state, robot1))
        self.add_tactic(robot2.id, DemoFollowRobot(self.game_state, robot2, args=[robot1.id]))
        self.add_tactic(robot3.id, DemoFollowRobot(self.game_state, robot3, args=[robot2.id]))

        for player in self.game_state.my_team.available_players.values():
            if not (player.id == robot1.id or player.id == robot2.id or player.id == robot3.id):
                self.add_tactic(player.id, Stop(self.game_state, player))




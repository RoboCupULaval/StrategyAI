# Under MIT License, see LICENSE.txt

from functools import partial
from random import shuffle

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.DemoFollowBall import DemoFollowBall
from ai.STA.Tactic.DemoFollowRobot import DemoFollowRobot
from ai.STA.Tactic.DemoFollowTarget import DemoFollowTarget
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.Joystick import Joystick


class BambaFollow(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        robot1 = 4
        robot2 = 2
        robot3 = 3
        args = [-1, -1, 0]
        self.add_tactic(robot1, DemoFollowBall(self.game_state, robot1))
        self.add_tactic(robot2, DemoFollowRobot(self.game_state, robot2, args=[robot1]))
        self.add_tactic(robot3, DemoFollowRobot(self.game_state, robot3, args=[robot2]))

        for i in range(PLAYER_PER_TEAM):
            if not (i == robot1 or i == robot2 or i == robot3):
                self.add_tactic(i, Stop(self.game_state, i))




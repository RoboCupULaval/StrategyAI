# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.ProtectZone import ProtectZone
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.mark import Mark
from . Strategy import Strategy


class SimpleDefense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        robot1 = 3
        robot2 = 5
        robot3 = 4
        goal = Pose(Position(-1636, 0))
        self.add_tactic(robot1, GoalKeeper(self.game_state, robot1))
        self.add_tactic(robot2, Mark(self.game_state, robot2))
        self.add_tactic(robot3, GoKick(self.game_state, robot3, goal))

        for i in range(PLAYER_PER_TEAM):
            if not (i == robot1 or i == robot2 or i == robot3):
                self.add_tactic(i, Stop(self.game_state, i))

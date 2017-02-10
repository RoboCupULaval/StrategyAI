# Under MIT license, see LICENSE.txt

from math import pi
from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.Node import Node
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags

__author__ = 'RoboCupULaval'


class TestAstarStrategy(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.add_tactic(0, GoalKeeper(self.game_state, 0))

        self.add_tactic(1, GoToPositionNoPathfinder(self.game_state, 1, Pose(Position(0, 0), 0)))
        self.add_tactic(2, GoToPositionNoPathfinder(self.game_state, 2, Pose(Position(4000, 2500), 0)))
        self.add_tactic(3, GoToPositionNoPathfinder(self.game_state, 3, Pose(Position(-4000, -2500), 0)))
        self.add_tactic(4, GoToPositionNoPathfinder(self.game_state, 4, Pose(Position(4000, -2500), 0)))
        self.add_tactic(5, GoToPositionNoPathfinder(self.game_state, 5, Pose(Position(-4000, 2500), 0)))


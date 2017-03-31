# Under MIT License, see LICENSE.txt

from functools import partial
from random import shuffle

from RULEngine.Util.Pose import Position, Pose
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags


class RobocupChoreography(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        positions_on_xaxis = [Pose(Position(-300*3, 0), 1.57), Pose(Position(-300*2, 0), 1.57), Pose(Position(-300, 0), 1.57), Pose(Position(300, 0), 1.57),
                     Pose(Position(2*300, 0), 1.57), Pose(Position(3*300, 0), 1.57)]
        shuffle(positions_on_xaxis)
        positions_on_yaxis = [Pose(Position(0, -300 * 3), 0), Pose(Position(0, -300 * 2), 0), Pose(Position(0, -300), 0),
                     Pose(Position(0, 300), 0), Pose(Position(0, 2 * 300), 0), Pose(Position(0, 3 * 300), 0)]
        shuffle(positions_on_yaxis)
        for i in range(PLAYER_PER_TEAM):
            self.add_tactic(i, GoToPositionPathfinder(self.game_state, i, positions_on_xaxis[i]))
            self.add_tactic(i, GoToPositionPathfinder(self.game_state, i, positions_on_yaxis[i]))
            self.add_condition(i, 0, 1, partial(self.condition, i))
            self.add_condition(i, 1, 0, partial(self.condition, i))


    def condition(self, i):
        for k in range(PLAYER_PER_TEAM):
            if not self.graphs[k].get_current_tactic().status_flag == Flags.SUCCESS:
                return False
        return True


# Under MIT license, see LICENSE.txt

import math

from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.PassBall import PassBall
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.ReceivePass import ReceivePass
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Tactic.GoalKeeper import GoalKeeper

__author__ = 'RoboCupULaval'


class TestPasses(Strategy):
    """
    Stratégie permettant de tester les passes.
    Robot 0: Gardien, une seule tactique.
    Robot 1: Fait la passe.
    Robot 2: Reçoit la passe.
    Robot 3 à 5: Ne bouge pas, une seule tactique.
    """
    def __init__(self, game_state):
        super().__init__(game_state)
        self.passer_id = 1
        self.receiver_id = 2
        self.receiver_pose = self.game_state.get_player_pose(self.receiver_id)

        self.add_tactic(0, GoalKeeper(self.game_state, 0))

        self.add_tactic(self.passer_id, GoGetBall(self.game_state, self.passer_id, self.receiver_pose))
        self.add_tactic(self.passer_id, PassBall(self.game_state, self.passer_id, self.receiver_pose.position))
        self.add_condition(self.passer_id, 0, 1, self.passer_has_ball)

        self.add_tactic(self.receiver_id, Stop(self.game_state, self.receiver_id))
        self.add_tactic(self.receiver_id, ReceivePass(self.game_state, self.receiver_id))
        self.add_condition(self.receiver_id, 0, 1, self.is_ball_moving)

        for i in range(3, PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

    def passer_has_ball(self):
        return self.graphs[self.passer_id].nodes[0].tactic.status_flag == Flags.SUCCESS

    def is_ball_moving(self):
        ball_velocity = self.game_state.get_ball_velocity()
        return math.sqrt(ball_velocity.x**2 + ball_velocity.y**2) >= 5  # FIXME: valeur random, à mesurer

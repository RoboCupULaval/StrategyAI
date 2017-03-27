# Under MIT license, see LICENSE.txt

import math

from RULEngine.Util.constant import PLAYER_PER_TEAM
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle, get_distance
from ai.STA.Strategy.Strategy import Strategy
from ai.STA.Tactic.PassBall import PassBall
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.ReceivePass import ReceivePass
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.RotateAround import RotateAround
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
        self.passer_position = self.game_state.get_player_pose(self.passer_id).position
        self.receiver_id = 2
        self.receiver_pose = self.game_state.get_player_pose(self.receiver_id)
        self.ball_position = self.game_state.get_ball_position()

        self.add_tactic(0, GoalKeeper(self.game_state, 0))

        self.add_tactic(self.passer_id, GoGetBall(self.game_state, self.passer_id, self.receiver_pose, None))
        self.add_tactic(self.passer_id, RotateAround(self.game_state, self.passer_id, self.ball_position,
                                                     self.receiver_pose.position))
        self.add_tactic(self.passer_id, PassBall(self.game_state, self.passer_id, self.receiver_pose, None))
        self.add_condition(self.passer_id, 0, 1, self.passer_has_ball)
        self.add_condition(self.passer_id, 1, 2, self.ready_to_pass)
        self.add_condition(self.passer_id, 2, 0, self.pass_failed)

        p = Pose(self.receiver_pose.position, get_angle(self.receiver_pose.position, self.ball_position))
        self.add_tactic(self.receiver_id, GoToPositionNoPathfinder(self.game_state, self.receiver_id, p))
        self.add_tactic(self.receiver_id, ReceivePass(self.game_state, self.receiver_id, p))
        self.add_condition(self.receiver_id, 0, 1, self.pass_was_made)

        for i in range(3, PLAYER_PER_TEAM):
            self.add_tactic(i, Stop(self.game_state, i))

    def passer_has_ball(self):
        return self.graphs[self.passer_id].nodes[0].tactic.status_flag == Flags.SUCCESS

    def passer_ready(self):
        return self.graphs[self.passer_id].nodes[1].tactic.status_flag == Flags.SUCCESS

    def receiver_ready(self):
        return self.graphs[self.receiver_id].nodes[0].tactic.status_flag == Flags.SUCCESS

    def ready_to_pass(self):
        return self.passer_ready() and self.receiver_ready()

    def pass_failed(self):
        return self.graphs[self.passer_id].nodes[2].tactic.status_flag == Flags.FAILURE

    def pass_was_made(self):
        ball_position = self.game_state.get_ball_position()
        passer_position = self.game_state.get_player_position(self.passer_id)
        #return self.passer_ready() and get_distance(ball_position, passer_position) >= 300  # FIXME: valeur random, à mesurer
        return self.graphs[self.passer_id].nodes[2].tactic.status_flag == Flags.SUCCESS

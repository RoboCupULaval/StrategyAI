# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np
from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.ProtectZone import ProtectZone
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.capture import Capture
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.intercept import Intercept
from ai.STA.Tactic.mark import Mark
from . Strategy import Strategy


class SimpleDefense(Strategy):
    def __init__(self, p_game_state):
        super().__init__(p_game_state)
        self.robot1 = 3
        self.robot2 = 5
        self.robot3 = 4
        goal1 = Pose(Position(-1636, 0))
        goal2 = Pose(Position(1636, 0))
        self.add_tactic(self.robot1, GoalKeeper(self.game_state, self.robot1))

        self.add_tactic(self.robot2, Intercept(self.game_state, self.robot2))
        self.add_tactic(self.robot2, GoKick(self.game_state, self.robot2, goal2))
        self.add_condition(self.robot2, 0, 1, partial(self.is_ball_closest_to_player, self.robot2))
        self.add_condition(self.robot2, 1, 0, partial(self.is_ball_closest_to_player, self.robot3))

        self.add_tactic(self.robot3, GoKick(self.game_state, self.robot3, goal1))
        self.add_tactic(self.robot3, Intercept(self.game_state, self.robot3, goal2))
        self.add_condition(self.robot3, 0, 1, partial(self.is_ball_closest_to_player, self.robot2))
        self.add_condition(self.robot3, 1, 0, partial(self.is_ball_closest_to_player, self.robot3))

        for i in range(PLAYER_PER_TEAM):
            if not (i == self.robot1 or i == self.robot2 or i == self.robot3):
                self.add_tactic(i, Stop(self.game_state, i))

    def is_ball_closest_to_player(self, player_id):
        player = self.game_state.get_player_position(player_id).conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        dist_ref = np.linalg.norm(player - ball)

        for i in range(PLAYER_PER_TEAM):
            if not i == player_id:
                dist = np.linalg.norm(self.game_state.get_player_position(i).conv_2_np() - ball)
                if dist < dist_ref:
                    return False
        return True


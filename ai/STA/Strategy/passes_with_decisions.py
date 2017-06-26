# Under MIT License, see LICENSE.txt

import numpy as np
from functools import partial

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Position, Pose
from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Strategy.Strategy import Strategy
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.capture import Capture
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.pass_to_player import PassToPlayer
from ai.STA.Tactic.tactic_constants import Flags


class PassesWithDecisions(Strategy):

    def __init__(self, p_game_state):
        super().__init__(p_game_state)

        self.passing_ID = 5
        self.player_ID_no1 = 2
        self.player_ID_no2 = 3
        self.goal_ID = None
        self.goal = (Pose(Position(self.game_state.const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0))

        self.add_tactic(self.passing_ID, Stop(self.game_state, self.passing_ID))
        self.add_tactic(self.passing_ID, PassToPlayer(self.game_state, self.passing_ID, target_id=self.player_ID_no1))
        self.add_tactic(self.passing_ID, PassToPlayer(self.game_state, self.passing_ID, target_id=self.player_ID_no2))
        self.add_tactic(self.passing_ID, GoKick(self.game_state, self.passing_ID, self.goal))

        self.add_condition(self.passing_ID, 0, 1, partial(self.is_best_receiver, self.player_ID_no1))
        self.add_condition(self.passing_ID, 0, 2, partial(self.is_best_receiver, self.player_ID_no2))
        self.add_condition(self.passing_ID, 0, 3, partial(self.is_best_receiver, None))

        self.add_condition(self.passing_ID, 1, 0, partial(self.condition, self.passing_ID))
        self.add_condition(self.passing_ID, 2, 0, partial(self.condition, self.passing_ID))
        self.add_condition(self.passing_ID, 3, 0, partial(self.condition, self.passing_ID))

        for i in range(PLAYER_PER_TEAM):
            if not (i == self.passing_ID):
                self.add_tactic(i, Stop(self.game_state, i))

    def condition(self, i):
        # print(i)
        # print(self.graphs[self.passing_ID].get_current_tactic())
        return self.graphs[i].get_current_tactic().status_flag == Flags.SUCCESS

    def is_best_receiver(self, receiver_id):
        if self.condition(receiver_id):
            if best_passing_option(self.passing_ID) == receiver_id:
                return True
        return False

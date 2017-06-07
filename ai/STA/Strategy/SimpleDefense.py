# Under MIT license, see LICENSE.txt
from functools import partial

import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.ProtectZone import ProtectZone
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.capture import Capture
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.intercept import Intercept
from ai.STA.Tactic.mark import Mark
from ai.states.game_state import GameState
from . Strategy import Strategy


class SimpleDefense(Strategy):
    def __init__(self, game_state: GameState):
        super().__init__(game_state)
        robot1 = self.game_state.my_team.available_players[5]
        robot2 = self.game_state.my_team.available_players[3]
        robot3 = self.game_state.my_team.available_players[4]
        goal1 = Pose(Position(-1636, 0))
        goal2 = Pose(Position(1636, 0))
        self.add_tactic(robot1.id, GoalKeeper(self.game_state, robot1))

        self.add_tactic(robot2.id, Intercept(self.game_state, robot2))
        self.add_tactic(robot2.id, GoKick(self.game_state, robot2, goal2))
        self.add_condition(robot2.id, 0, 1, partial(self.is_ball_closest_to_player, robot2))
        self.add_condition(robot2.id, 1, 0, partial(self.is_ball_closest_to_player, robot3))

        self.add_tactic(robot3.id, GoKick(self.game_state, robot3, goal1))
        self.add_tactic(robot3.id, Intercept(self.game_state, robot3, goal2))
        self.add_condition(robot3.id, 0, 1, partial(self.is_ball_closest_to_player, robot2))
        self.add_condition(robot3.id, 1, 0, partial(self.is_ball_closest_to_player, robot3))

        for player in self.game_state.my_team.available_players.values():
            if not (player.id == robot1.id or player.id == robot2.id or player.id == robot3.id):
                self.add_tactic(player.id, Stop(self.game_state, player))

    def is_ball_closest_to_player(self, player: OurPlayer):
        player_pos = player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        dist_ref = np.linalg.norm(player_pos - ball)

        for p in self.game_state.my_team.available_players.values():
            if not p == player.id:
                dist = np.linalg.norm(p.pose.position.conv_2_np() - ball)
                if dist < dist_ref:
                    return False
        return True


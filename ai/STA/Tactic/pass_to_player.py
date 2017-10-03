# Under MIT licence, see LICENCE.txt
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class PassToPlayer(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), target_id=1, args=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.last_time = time.time()
        self.target_id = target_id

    def kick_charge(self):
        if time.time() - self.last_time > COMMAND_DELAY:
            self.next_state = self.get_behind_ball
            self.last_time = time.time()

        return AllStar(self.game_state, self.player, **{"charge_kick": True, "dribbler_on": 1})

    def get_behind_ball(self):
        self.status_flag = Flags.WIP
        player = self.player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        target = self.game_state.get_player_position(self.target_id, True).conv_2_np()

        vector_player_2_ball = ball - player
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)

        if self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(),
                        Position.from_np(target), 120, pathfinder_on=True)

    def grab_ball(self):
        if self._get_distance_from_ball() < 120:
            self.next_state = self.kick
            self.last_time = time.time()
        elif self._is_player_towards_ball_and_target(-0.9):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return Grab(self.game_state, self.player)

    def kick(self):
        if self._get_distance_from_ball() > 300:
            self.next_state = self.halt
            self.last_time = time.time()
        elif time.time() - self.last_time < COMMAND_DELAY:
            self.next_state = self.kick
        else:
            self.next_state = self.kick_charge
        return Kick(self.game_state, self.player, 1, self.target)

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return get_distance(self.player.pose.position, self.game_state.get_ball_position())

    def _is_player_towards_ball_and_target(self, fact=-0.99):
        player = self.player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        target = self.game_state.get_player_position(self.target_id, True).conv_2_np()

        vector_player_2_ball = ball - player
        vector_target_2_ball = ball - target
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_player_2_ball, vector_target_2_ball) < fact:
            if np.dot(vector_player_dir, vector_target_2_ball) < fact:
                return True
        return False

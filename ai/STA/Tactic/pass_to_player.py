# Under MIT licence, see LICENCE.txt

import time

import numpy as np

from Util import Pose, Position, AICommand
from Util.constant import BALL_RADIUS, ROBOT_RADIUS
from Util.position import Position

from ai.GameDomainObjects import Player
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class PassToPlayer(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), target_id=1, args=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.last_time = time.time()
        self.target_id = target_id

    def kick_charge(self):
        if time.time() - self.last_time > COMMAND_DELAY:
            self.next_state = self.get_behind_ball
            self.last_time = time.time()

        # todo charge kick here please/ask Simon what kicktype is supposed to be
        return AICommand(self.player.id, kick_type=1, dribbler_active=True)

    def get_behind_ball(self):
        self.status_flag = Flags.WIP
        player = self.player.pose.position
        ball = self.game_state.get_ball_position()
        target = self.game_state.get_player_position(self.target_id, True)

        vector_player_2_ball = ball - player
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)

        if self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(),
                        Position.from_array(target), 120, pathfinder_on=True)

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
        return (self.player.pose.position - self.game_state.get_ball_position()).norm

    def _is_player_towards_ball_and_target(self, fact=-0.99):
        player = self.player.pose.position
        ball = self.game_state.get_ball_position()
        target = self.game_state.get_player_position(self.target_id, True)

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

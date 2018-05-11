# Under MIT licence, see LICENCE.txt

import time
from typing import Optional, List

import numpy as np

from Util import Pose, Position, AICommand
from Util.constant import BALL_RADIUS, ROBOT_RADIUS, KickForce

from ai.GameDomainObjects import Player
from Util.ai_command import Idle, CmdBuilder, MoveTo
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class PassToPlayer(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: Optional[List[str]]=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.last_time = time.time()
        if args:
            self.target_id = int(args[0])
        else:
            self.target_id = 1

    def kick_charge(self):
        if time.time() - self.last_time > COMMAND_DELAY:
            self.next_state = self.get_behind_ball
            self.last_time = time.time()

        return CmdBuilder().addKick().addForceDribbler().build()

    def get_behind_ball(self):
        self.status_flag = Flags.WIP
        player = self.player.pose.position
        ball = self.game_state.ball_position
        target = self.game_state.get_player_position(self.target_id)

        vector_player_2_ball = ball - player
        vector_player_2_ball /= vector_player_2_ball.norm

        if self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return GoBehind(self.player, self.game_state.ball_position, target, 120)

    def grab_ball(self):
        if self._get_distance_from_ball() < 120:
            self.next_state = self.kick
            self.last_time = time.time()
        elif self._is_player_towards_ball_and_target(-0.9):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return MoveTo(Pose(self.game_state.ball.position, self.player.pose.orientation))

    def kick(self):
        if self._get_distance_from_ball() > 300:
            self.next_state = self.halt
            self.last_time = time.time()
        elif time.time() - self.last_time < COMMAND_DELAY:
            self.next_state = self.kick
        else:
            self.next_state = self.kick_charge
        return CmdBuilder().addKick(KickForce.HIGH).addMoveTo(self.target).build()

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _is_player_towards_ball_and_target(self, fact=-0.99):
        player = self.player.pose.position
        ball = self.game_state.ball_position
        target = self.game_state.get_player_position(self.target_id)

        vector_player_2_ball = ball - player
        vector_target_2_ball = ball - target
        vector_player_2_ball /= vector_player_2_ball.norm
        vector_target_2_ball /= vector_target_2_ball.norm
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_player_2_ball.array, vector_target_2_ball.array) < fact:
            if np.dot(vector_player_dir, vector_target_2_ball.array) < fact:
                return True
        return False

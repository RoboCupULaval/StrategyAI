# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np

from RULEngine.GameDomainObjects.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.STA.Action.Idle import Idle
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class Intercept(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.go_between_ball_and_target
        self.next_state = self.go_between_ball_and_target

    def go_between_ball_and_target(self):
        self.status_flag = Flags.WIP
        ball = self.game_state.get_ball_position()
        ball_velocity = self.game_state.get_ball_velocity().conv_2_np()
        if np.linalg.norm(ball_velocity) > 50:
            self.target = Pose(Position.from_np(ball.conv_2_np() - ball_velocity), 0)
            dist_behind = np.linalg.norm(ball_velocity) + 1/np.sqrt(np.linalg.norm(ball_velocity))
        else:
            self.target = None
            dist_behind = 250
        if self.target is None:
            self.target = Pose(self.game_state.const["FIELD_THEIR_GOAL_MID_GOAL"], 0)
        if self._is_player_towards_ball_and_target():
                self.next_state = self.grab_ball
        else:
            self.next_state = self.go_between_ball_and_target

        return GoBehind(self.game_state, self.player, ball, self.target.position, dist_behind)

    def _is_player_towards_ball_and_target(self):

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        target_x = self.target.position.x
        target_y = self.target.position.y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_target_2_ball = np.array([ball_x - target_x, ball_y - target_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_player_2_ball, vector_target_2_ball) < - 0.99:
            if np.dot(vector_player_dir, vector_target_2_ball) < - 0.99:
                return True
        return False

    def grab_ball(self):
        if self._is_player_towards_ball():
            self.next_state = self.halt
        else:
            self.next_state = self.grab_ball
            self.status_flag = Flags.WIP
        return Grab(self.game_state, self.player)

    def _is_player_between_ball_and_target(self, fact=-0.99):
        player = self.player.pose.position.conv_2_np()
        target = self.target.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        target_to_ball = ball - target
        ball_to_player /= np.linalg.norm(ball_to_player)
        target_to_ball /= np.linalg.norm(target_to_ball)
        player_dir = np.array([np.cos(self.player.pose.orientation),
                               np.sin(self.player.pose.orientation)])
        if np.dot(ball_to_player, target_to_ball) < fact:
            if np.dot(player_dir, ball_to_player) < fact:
                return True
        return False

    def _is_player_towards_ball(self, fact=-0.99):
        player = self.player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        ball_to_player /= np.linalg.norm(ball_to_player)
        player_dir = np.array([np.cos(self.player.pose.orientation),
                               np.sin(self.player.pose.orientation)])
        if np.dot(player_dir, ball_to_player) < fact:
            return True
        return False

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

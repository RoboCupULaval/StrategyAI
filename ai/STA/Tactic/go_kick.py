import math as m
from typing import List, Union
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import compare_angle
from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 100
APPROACH_SPEED = 100
KICK_DISTANCE = 110
KICK_SUCCEED_THRESHOLD = 600
COMMAND_DELAY = 0.5


class GoKick(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: Union[int, float]=5,
                 auto_update_target=False):

        super().__init__(game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.cmd_last_time = time.time()
        self.kick_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.target_assignation_last_time = 0
        self.target = target
        if self.auto_update_target:
            self._find_best_passing_option()
        self.kick_force = kick_force
        self.ball_spacing = GRAB_BALL_SPACING
        self.tries_flag = 0
        self.grab_ball_tries = 0

    def kick_charge(self):
        if time.time() - self.cmd_last_time > COMMAND_DELAY:
            self.next_state = self.go_behind_ball
            self.cmd_last_time = time.time()
        tentative_command = {'charge_kick':True}
        return AllStar(self.game_state, self.player, other_args=tentative_command)

    def go_behind_ball(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.status_flag = Flags.WIP
        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING * 3)
        if (self.player.pose.position - distance_behind).norm() < 100 and abs(orientation - self.player.pose.orientation) < 0.1:
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            if self.auto_update_target:
                self._find_best_passing_option()
        collision_ball = self.tries_flag == 0
        return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                      collision_ball=True, cruise_speed=2, end_speed=0.2)

    def grab_ball(self):
        distance_to_kick = KICK_DISTANCE + self.grab_ball_tries * 10

        ball_position = self.game_state.get_ball_position()
        distance_behind = self.get_destination_behind_ball(GRAB_BALL_SPACING)
        orientation = (self.target.position - ball_position).angle()

        if self._get_distance_from_ball() < distance_to_kick:
            self.next_state = self.kick

        return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                     cruise_speed=2, charge_kick=True, end_speed=0.2, collision_ball=False)

    def kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.next_state = self.validate_kick
        self.tries_flag += 1
        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        return Kick(self.game_state, self.player, self.kick_force, Pose(ball_position, orientation), cruise_speed=2, end_speed=0)

    def validate_kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        if self.game_state.get_ball_velocity().norm() > 1000 or self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.kick
        else:
            self.status_flag = Flags.INIT
            self.next_state = self.go_behind_ball

        return Kick(self.game_state, self.player, self.kick_force, Pose(ball_position, orientation), cruise_speed=2, end_speed=0.2)

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi/30):
        ball_position = self.game_state.get_ball_position()
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle(), ball_to_player.angle(), abs_tol=abs_tol)

    def _find_best_passing_option(self):
        assignation_delay = (time.time() - self.target_assignation_last_time)

        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0, 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing):
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """

        delta_x = self.target.position.x - self.game_state.get_ball_position().x
        delta_y = self.target.position.y - self.game_state.get_ball_position().y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.game_state.get_ball_position().x - ball_spacing * np.math.cos(theta)
        y = self.game_state.get_ball_position().y - ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position
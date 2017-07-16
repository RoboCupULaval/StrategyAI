# Under MIT licence, see LICENCE.txt
import math as m
from typing import List, Union
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from RULEngine.Util.geometry import get_distance, compare_angle, wrap_to_pi
from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.rotate_around import RotateAround
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommandType
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 200
GRAB_BALL_SPACING = 220
APPROACH_SPEED = 100
KICK_DISTANCE = 90
KICK_SUCCEED_THRESHOLD = 300


class GoKick(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player : Instance du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, game_state: GameState, player: OurPlayer,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: Union[int, float]=3,
                 auto_update_target=False):

        Tactic.__init__(self, game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
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
        self.next_state = self.go_behind_ball
        return AllStar(self.game_state,
                       self.player,
                       charge_kick=True)

    def go_behind_ball(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.status_flag = Flags.WIP

        if self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            if self.auto_update_target:
                self._find_best_passing_option()


        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        distance_behind = self.get_destination_behind_ball()
        distance_to_goal = (distance_behind - self.player.pose.position).norm()
        if distance_to_goal > 150:
            go_behind_ball_speed = 1
        else:
            go_behind_ball_speed = distance_to_goal / 150
        if self.tries_flag == 0:
            return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                          collision_ball=True, cruise_speed=go_behind_ball_speed)
        else:
            return GoToPositionPathfinder(self.game_state, self.player, Pose(distance_behind, orientation),
                                          collision_ball=False, cruise_speed=go_behind_ball_speed)
        # return RotateAround(self.game_state,
        #                     self.player,
        #                     Pose(ball_position, orientation),
        #                     GO_BEHIND_SPACING,
        #                     pathfinder_on=True,
        #                     aiming=self.target,
        #                     rotation_speed=3 * m.pi,
        #                     speed_mode=True,
        #                     behind_target=distance_behind)

    def grab_ball(self):
        if self.grab_ball_tries == 0:
            if self._get_distance_from_ball() < KICK_DISTANCE:
                self.next_state = self.kick
        elif not self._is_player_towards_ball_and_target():
            self.next_state = self.go_behind_ball
            self.grab_ball_tries = 0
            print("reset")
        else:
            print(self._get_distance_from_ball())
            print(KICK_DISTANCE + self.grab_ball_tries * 10)
            print(self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10))
            if (self._get_distance_from_ball() < (KICK_DISTANCE + self.grab_ball_tries * 10)):
                self.next_state = self.kick



        # else:
        #     self.tries_flag = self.tries_flag + 1
        #     self.next_state = self.grab_ball
        #     self.grab_ball_tries = self.grab_ball_tries + 1

        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        distance_behind = self.get_destination_behind_ball()
        distance_to_goal = (distance_behind - self.player.pose.position).norm()
        if distance_to_goal > 150:
            go_behind_ball_speed = 1
        else:
            go_behind_ball_speed = distance_to_goal / 150
        return GoToPositionPathfinder(self.game_state, self.player, Pose(ball_position, orientation), cruise_speed=go_behind_ball_speed/1000)
        # return RotateAround(self.game_state,
        #                     self.player,
        #                     Pose(ball_position, orientation),
        #                     self.ball_spacing,
        #                     aiming=self.target,
        #                     rotation_speed=m.pi,
        #                     pathfinder_on=True,
        #                     speed_mode=True,
        #                     behind_target=distance_behind,
        #                     approach=True)

    def kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        self.next_state = self.validate_kick
        if not self._is_player_towards_ball_and_target():
            self.next_state = self.go_behind_ball
            self.grab_ball_tries = 0
            self.tries_flag = 0
            print("reset")

        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def validate_kick(self):
        if self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        # elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
        #     self.next_state = self.grab_ball
        elif self.kick_last_time:
            self.next_state = self.kick

        return Idle(self.game_state, self.player)

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi/20):
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

    def get_destination_behind_ball(self):
        """
            Calcule le point situé à  x pixels derrière la position 1 par rapport à la position 2
            :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
            """

        delta_x = self.target.position.x - self.game_state.get_ball_position().x
        delta_y = self.target.position.y - self.game_state.get_ball_position().y
        theta = np.math.atan2(delta_y, delta_x)

        x = self.game_state.get_ball_position().x - self.ball_spacing * np.math.cos(theta)
        y = self.game_state.get_ball_position().y - self.ball_spacing * np.math.sin(theta)

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        if np.sqrt((player_x - x) ** 2 + (player_y - y) ** 2) < 50:
            x -= np.math.cos(theta) * 2
            y -= np.math.sin(theta) * 2
        destination_position = Position(x, y)

        return destination_position

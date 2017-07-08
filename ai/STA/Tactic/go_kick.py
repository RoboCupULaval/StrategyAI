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
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommandType
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1


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
        self.cmd_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.target_assignation_last_time = None
        self.target = target
        #self._find_best_passing_option()
        self.kick_force = kick_force
        self.ball_position = self.game_state.get_ball_position()
        self.ball_spacing = 100

    def kick_charge(self):
        print('Charging')
        if time.time() - self.cmd_last_time > COMMAND_DELAY:
            self.next_state = self.go_behind_ball
            self.cmd_last_time = time.time()

        return AllStar(self.game_state,
                       self.player,
                       charge_kick=True,
                       dribbler_on=1)

    def go_behind_ball(self):
        self.ball_spacing = 100
        self.status_flag = Flags.WIP
        print('Going behind ball', self._is_player_towards_ball_and_target(), self._get_distance_from_ball())
        if self._is_player_towards_ball_and_target() and self._get_distance_from_ball() < 250:
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            #  self._find_best_passing_option()

        orientation = (self.target.position - self.ball_position).angle()
        return RotateAround(self.game_state,
                            self.player,
                            Pose(self.game_state.get_ball_position(), orientation),
                            150,
                            pathfinder_on=True,
                            heading=self.target)

    def grab_ball(self):
        print('Grabbing ball', self._is_player_towards_ball_and_target(), self._get_distance_from_ball())
        if self._get_distance_from_ball() < 120:
            self.next_state = self.kick
            self.cmd_last_time = time.time()
        elif self._is_player_towards_ball_and_target():
            self.ball_spacing *= 0.98
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball

        orientation = (self.target.position - self.ball_position).angle()
        return RotateAround(self.game_state,
                            self.player,
                            Pose(self.ball_position, orientation),
                            self.ball_spacing,
                            heading=self.target)

    def kick(self):
        print('Kicking')
        if self._get_distance_from_ball() > 200:
            self.next_state = self.halt
            self.cmd_last_time = time.time()
        elif time.time() - self.cmd_last_time < COMMAND_DELAY:
            self.next_state = self.kick
        else:
            self.next_state = self.kick_charge
        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def halt(self):  # FAIRE CECI DANS TOUTE LES TACTIQUES
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return get_distance(self.player.pose.position,
                            self.game_state.get_ball_position())

    def _is_player_towards_ball_and_target(self, abs_tol=m.pi/20):

        target_to_ball = self.ball_position - self.target.position
        ball_to_player = self.player.pose.position - self.ball_position
        print(target_to_ball.angle(), ball_to_player.angle())
        print(self.ball_position.angle(), self.player.pose.position.angle(), self.target.position.angle())
        return compare_angle(target_to_ball.angle(), ball_to_player.angle(), abs_tol=abs_tol)  # True if heading is right

    def _find_best_passing_option(self):
        if (self.auto_update_target
            and (self.target_assignation_last_time is None
                or time.time() - self.target_assignation_last_time > TARGET_ASSIGNATION_DELAY)):
            tentative_target_id = best_passing_option(self.player)
            print(tentative_target_id)
            if tentative_target_id is None:
                self.target = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))
            self.target_assignation_last_time = time.time()

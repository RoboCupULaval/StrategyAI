# Under MIT licence, see LICENCE.txt
import math as m
from typing import List, Union
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import are_collinear
from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.rotate_around import RotateAround
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 250
GRAB_BALL_SPACING = 120
APPROACH_SPEED = 100
KICK_DISTANCE = 105
KICK_SUCCEED_THRESHOLD = 200


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

    def __init__(self,
                 game_state: GameState,
                 player: OurPlayer,
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
        return RotateAround(self.game_state,
                            self.player,
                            Pose(ball_position, orientation),
                            GO_BEHIND_SPACING,
                            pathfinder_on=True,
                            aiming=self.target,
                            rotation_speed=6*m.pi)

    def grab_ball(self):
        if self._get_distance_from_ball() < KICK_DISTANCE:
            self.next_state = self.kick
        elif self._is_player_towards_ball_and_target():
            self.ball_spacing -= APPROACH_SPEED * self.game_state.get_delta_t()
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball

        ball_position = self.game_state.get_ball_position()
        orientation = (self.target.position - ball_position).angle()
        return RotateAround(self.game_state,
                            self.player,
                            Pose(ball_position, orientation),
                            self.ball_spacing,
                            aiming=self.target,
                            rotation_speed=4*m.pi)

    def kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        if self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.grab_ball
        else:
            self.next_state = self.validate_kick

        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def validate_kick(self):
        if self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        elif self.kick_last_time - time.time() < VALIDATE_KICK_DELAY:
            self.next_state = self.validate_kick
        elif self.kick_last_time:
            self.next_state = self.kick_charge

        return Idle(self.game_state, self.player)

    def kick(self):
        self.ball_spacing = GRAB_BALL_SPACING
        if self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD:
            self.next_state = self.halt
        else:
            self.kick_last_time = time.time()
            self.next_state = self.validate_kick

        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _is_player_towards_ball_and_target(self):
        ball_position = self.game_state.get_ball_position()
        return are_collinear(self.player.pose.position, ball_position, self.target.position, abs_tol=m.pi/20)

    def _find_best_passing_option(self):

        assignation_delay = (time.time() - self.target_assignation_last_time)

        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0, 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

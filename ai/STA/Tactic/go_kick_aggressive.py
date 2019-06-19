# Under MIT licence, see LICENCE.txt

import time
from typing import List

import numpy as np

from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle
from Util.constant import ROBOT_CENTER_TO_KICKER, BALL_RADIUS, KickForce
from Util.geometry import compare_angle, normalize
from ai.Algorithm.evaluation_module import best_passing_option
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.executors.pathfinder_module import WayPoint
from ai.states.game_state import GameState

VALIDATE_KICK_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

GO_BEHIND_SPACING = 250
GRAB_BALL_SPACING = 200
APPROACH_SPEED = 100
KICK_DISTANCE = 100
KICK_SUCCEED_THRESHOLD = 600
COMMAND_DELAY = 0.5


# noinspection PyArgumentList,PyUnresolvedReferences,PyUnresolvedReferences
class GoKickAggressive(Tactic):
    def __init__(self, game_state: GameState, player: Player,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: KickForce=KickForce.HIGH,
                 auto_update_target=False,
                 go_behind_distance=GO_BEHIND_SPACING):

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
        self.go_behind_distance = go_behind_distance
        self.tries_flag = 0
        self.grab_ball_tries = 0
        self.points_sequence = []

    def main_state(self):
        self.status_flag = Flags.WIP
        self.next_state = self.main_state
        if self.auto_update_target:
            self._find_best_passing_option()
        orientation = (self.target.position - self.game_state.ball_position).angle
        player_to_target = (self.target.position - self.player.pose.position)
        dist_from_ball = (self.player.position - self.game_state.ball_position).norm

        ball_speed = self.game_state.ball.velocity.norm
        ball_speed_vector = normalize(self.game_state.ball.velocity)
        ball_speed_modifier = (ball_speed / 1000)
        effective_ball_spacing = GO_BEHIND_SPACING * 4

        position_behind_ball_for_approach = self.get_destination_behind_ball(effective_ball_spacing) + ball_speed_vector * ball_speed_modifier
        position_behind_ball_for_grab = self.game_state.ball_position - normalize(player_to_target) * GRAB_BALL_SPACING
        position_behind_ball_for_kick = self.game_state.ball_position + normalize(player_to_target) * KICK_DISTANCE
        self.points_sequence = []
        if self.is_able_to_grab_ball_directly(0.9):
            if compare_angle(self.player.pose.orientation, orientation, abs_tol=0.1):

                return CmdBuilder().addMoveTo(Pose(position_behind_ball_for_kick, orientation),
                                              ball_collision=False, cruise_speed=3).addKick(self.kick_force).\
                    addForceDribbler().build()
            cruise_speed = 1
            self.points_sequence = [WayPoint(position_behind_ball_for_grab, ball_collision=False)]
            return CmdBuilder().addMoveTo(Pose(position_behind_ball_for_kick, orientation),
                                          ball_collision=False,
                                          way_points=self.points_sequence,
                                          cruise_speed=cruise_speed).addForceDribbler().build()
        else:
            self.points_sequence = [WayPoint(position_behind_ball_for_approach, ball_collision=True),
                                    WayPoint(position_behind_ball_for_grab, ball_collision=False)]

        return CmdBuilder().addMoveTo(Pose(position_behind_ball_for_kick, orientation),
                                      ball_collision=False,
                                      way_points=self.points_sequence,
                                      cruise_speed=3).build()

    def kick_charge(self):
        if time.time() - self.cmd_last_time > COMMAND_DELAY:

            self.next_state = self.main_state

            self.cmd_last_time = time.time()

        return CmdBuilder().addChargeKicker().build()

    def kick(self):
        self.next_state = self.validate_kick
        self.tries_flag += 1

        player_to_target = (self.target.position - self.player.pose.position)
        behind_ball = self.game_state.ball_position + normalize(player_to_target) * (BALL_RADIUS + ROBOT_CENTER_TO_KICKER)
        orientation = (self.target.position - self.game_state.ball_position).angle

        return CmdBuilder().addMoveTo(Pose(behind_ball, orientation),
                                      ball_collision=False,
                                      cruise_speed=3).addKick(self.kick_force).build()

    def validate_kick(self):
        if (self.game_state.ball_velocity.norm > 600) or (self._get_distance_from_ball() > KICK_SUCCEED_THRESHOLD):
            self.next_state = self.halt
        elif self._get_distance_from_ball() < GRAB_BALL_SPACING * 1.25:
            self.next_state = self.kick
        else:
            self.next_state = self.main_state

        return CmdBuilder().build()

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.ball_position).norm

    def _find_best_passing_option(self):
        assignation_delay = (time.time() - self.target_assignation_last_time)

        if assignation_delay > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose.from_values(GameState().field.their_goal_x, 0, 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))

            self.target_assignation_last_time = time.time()

    def get_destination_behind_ball(self, ball_spacing) -> Position:
        """
         Compute the point which is at ball_spacing mm behind the ball from the target.
        """
        dir_ball_to_target = normalize(self.target.position - self.game_state.ball.position)

        return self.game_state.ball.position - dir_ball_to_target * ball_spacing

    def is_able_to_grab_ball_directly(self, threshold):
        # plus que le threshold est gors (1 max), plus qu'on veut que le robot soit direct deriere la balle.
        vec_target_to_ball = normalize(self.game_state.ball.position - self.target.position)
        alignement_behind = np.dot(vec_target_to_ball.array,
                                   (normalize(self.player.position - self.game_state.ball_position)).array)
        return threshold < alignement_behind


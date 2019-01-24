# Under MIT licence, see LICENCE.txt

import numpy as np
from typing import Optional

from Util import Pose, Position
from Util.ai_command import CmdBuilder, Idle, MoveTo
from Util.constant import ROBOT_RADIUS
from Util.geometry import compare_angle, normalize, perpendicular, closest_point_on_line, Line, closest_point_on_segment

from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags

from ai.GameDomainObjects import Player
from ai.states.game_state import GameState

SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK = ROBOT_RADIUS + 200


class ReceivePass(Tactic):

    def __init__(self, game_state: GameState, player: Player, target: Optional[Pose]=None):
      
        super().__init__(game_state, player, target)
        self.current_state = self.initialize
        self.next_state = self.initialize

    def initialize(self):
        self.status_flag = Flags.WIP
        self.next_state = self.intercept
        return Idle

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle

    def intercept(self):
        ball = self.game_state.ball
        if self.game_state.field.is_outside_wall_limit(ball.position):
            self.logger.info("The ball has left the field")
            self.next_state = self.go_away_from_ball
            return Idle

        if self.game_state.ball.is_immobile():
            self.logger.info("The ball is not moving, success?")
            self.next_state = self.go_away_from_ball
            return Idle

        if (ball.position - self.player.position).norm < ROBOT_RADIUS + 50:
            self.logger.info("The ball about to touch us, success?")
            self.next_state = self.go_away_from_ball
            return Idle

        # Find the point where the ball will leave the field
        ball_trajectory = Line(ball.position, ball.position + ball.velocity)
        intersection_with_field = self.game_state.field.area.intersect_with_line(ball_trajectory)

        where_ball_enter_leave_field = None
        for inter in intersection_with_field:
            # If this is the intersection that have the same direction as ball.velocity
            if (inter - ball.position).dot(ball.velocity) > 0:
                where_ball_enter_leave_field = inter
                break

        if where_ball_enter_leave_field is None:
            self.logger.info("The ball is somehow inside and outside the field")
            self.next_state = self.halt

        # The robot can intercepts the ball by leaving the field, thus we must add a ROBOT_RADIUS
        ball_to_leave_field = Line(ball.position, where_ball_enter_leave_field)
        end_segment = where_ball_enter_leave_field + ball_to_leave_field.direction * ROBOT_RADIUS

        intersect_pts = closest_point_on_segment(self.player.position,
                                                 ball.position, end_segment)

        if (self.player.position - intersect_pts).norm < ROBOT_RADIUS:
            best_orientation = (ball.position - end_segment).angle
        else:
            # We move a bit faster, if we keep our orientation
            best_orientation = self.player.pose.orientation
        return MoveTo(Pose(intersect_pts, best_orientation),
                      cruise_speed=3,
                      end_speed=0,
                      ball_collision=False)

    def go_away_from_ball(self):
        """
        If the ball have been intersect, we should switch directly to go_kick.
        However go_kick does not like been initiated near the ball and will immediately kick it.
        To prevent this we do a simple go_behind_ball with the kicker off BEFORE switching to go_kick
        """
        ball_position = self.game_state.ball.position
        player_to_ball = ball_position - self.player.position
        if player_to_ball.norm > SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK:
            self.next_state = self.halt
            return self.next_state()

        target = self.game_state.field.their_goal  # We want a general orientation, go_kick will do the alignment
        away_position = normalize(ball_position - target) * SAFE_DISTANCE_TO_SWITCH_TO_GO_KICK + ball_position
        orientation = (target - self.game_state.ball.position).angle

        return CmdBuilder().addMoveTo(Pose(away_position, orientation),
                                      cruise_speed=3,
                                      end_speed=0,
                                      ball_collision=True)\
                           .addChargeKicker().build()


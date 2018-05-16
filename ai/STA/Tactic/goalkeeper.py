# Under MIT licence, see LICENCE.txt
from unittest.suite import _DebugResult

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory

__author__ = 'RoboCupULaval'

from typing import List

from Util import Pose, Position
from Util.ai_command import MoveTo, Idle
from Util.constant import ROBOT_RADIUS
from Util.geometry import intersection_line_and_circle, intersection_between_lines, \
    closest_point_on_segment
from ai.GameDomainObjects import Player

from ai.STA.Tactic.go_kick import GRAB_BALL_SPACING, GoKick

from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState



class GoalKeeper(Tactic):

    MOVING_BALL_VELOCITY = 50  # mm/s
    DANGER_BALL_VELOCITY = 600  # mm/s

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(),
                 penalty_kick=False, args: List[str]=None,):
        super().__init__(game_state, player, target, args)

        self.current_state = self.defense
        self.next_state = self.defense

        self.target = Pose(self.game_state.field.our_goal, np.pi)  # Ignore target argument, always go for our goal

        self.go_kick_tactic = None # Used by clear
        self.last_intersection = None # For debug

        self.OFFSET_FROM_GOAL_LINE = Position(ROBOT_RADIUS + 10, 0)
        self.GOAL_LINE = self.game_state.field.goal_line

    def defense_dumb(self):
        dest_y = self.game_state.ball.position.y \
                 * self.game_state.const["FIELD_GOAL_WIDTH"] / 2 / self.game_state.const["FIELD_Y_TOP"]
        position = self.game_state.field.our_goal - Position(ROBOT_RADIUS + 10, -dest_y)
        return MoveTo(Pose(position, np.pi))

    def defense(self):
        # Prepare to block the ball
        if self.game_state.field.is_ball_in_our_goal() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        if self._ball_going_toward_goal():
            self.next_state = self.intercept
            return self.intercept()  # no time to loose

        circle_radius = self.game_state.const["FIELD_GOAL_WIDTH"] / 2
        circle_center = self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE
        solutions = intersection_line_and_circle(circle_center,
                                                 circle_radius,
                                                 self.game_state.ball.position,
                                                 self._best_target_into_goal())
        # Their is one or two intersection on the circle, take the one on the field
        for solution in solutions:
            if solution.x < self.game_state.field.field_length / 2\
               and self.game_state.ball.position.x < self.game_state.field.field_length / 2:
                orientation_to_ball = (self.game_state.ball.position - self.player.position).angle
                return MoveTo(Pose(solution, orientation_to_ball),
                              cruise_speed=3,
                              end_speed=3)

        return MoveTo(Pose(self.game_state.field.our_goal, np.pi),
                      cruise_speed=3,
                      end_speed=3)

    def intercept(self):
        # Find the point where the ball will go
        if not self._ball_going_toward_goal() and not self.game_state.field.is_ball_in_our_goal():
            self.next_state = self.defense
        elif self.game_state.field.is_ball_in_our_goal() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        ball = self.game_state.ball
        pts = intersection_between_lines(self.GOAL_LINE.p1,
                                         self.GOAL_LINE.p2,
                                         ball.position,
                                         ball.position + ball.velocity)

        pts = closest_point_on_segment(pts, self.GOAL_LINE.p1, self.GOAL_LINE.p2)
        self.last_intersection = pts
        return MoveTo(Pose(pts, self.player.pose.orientation),  # It's a bit faster, to keep our orientation
                           cruise_speed=3,
                           end_speed=3,
                           ball_collision=False)

    def _ball_going_toward_goal(self):
        upper_angle = (self.game_state.ball.position - self.GOAL_LINE.p2).angle + 5 * np.pi / 180.0
        lower_angle = (self.game_state.ball.position - self.GOAL_LINE.p1).angle - 5 * np.pi / 180.0
        ball_speed = self.game_state.ball.velocity.norm
        return (ball_speed > self.DANGER_BALL_VELOCITY and self.game_state.ball.velocity.x > 0) or \
               (ball_speed > self.MOVING_BALL_VELOCITY and upper_angle <= self.game_state.ball.velocity.angle <= lower_angle)

    def clear(self):
        # Move the ball to outside of the penality zone
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state,
                                         self.player,
                                         auto_update_target=True,
                                         go_behind_distance=1.2*GRAB_BALL_SPACING) # make it easier
        if not self.game_state.field.is_ball_in_our_goal():
            self.next_state = self.defense
            self.go_kick_tactic = None
            return Idle
        else:
            return self.go_kick_tactic.exec()


    def _best_target_into_goal(self):
        # Find the bisection of the triangle made by the ball (a) and the two goals extremities(b, c)
        a = self.game_state.ball.position
        b = self.GOAL_LINE.p2
        c = self.GOAL_LINE.p1

        ab = a-b
        ac = a-c

        be = self.game_state.field.goal_width / (1 + ab.norm/ac.norm)

        return b + Position(0, -be)

    def debug_cmd(self):
        if self.current_state == self.defense:
            return DebugCommandFactory().line(self.game_state.ball.position,
                                                self._best_target_into_goal(),
                                                timeout=0.1)
        elif self.current_state == self.intercept and self.last_intersection is not None:
            return DebugCommandFactory().line(self.game_state.ball.position,
                                                self.last_intersection,
                                                timeout=0.1)
        else:
            return []



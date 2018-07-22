# Under MIT licence, see LICENCE.txt
from unittest.suite import _DebugResult

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory
from ai.Algorithm.evaluation_module import player_with_ball, player_pointing_toward_point, \
    player_pointing_toward_segment, closest_players_to_point

__author__ = 'RoboCupULaval'

from typing import List

from Util import Pose, Position
from Util.ai_command import MoveTo, Idle
from Util.constant import ROBOT_RADIUS, KEEPOUT_DISTANCE_FROM_GOAL, ROBOT_DIAMETER
from Util.geometry import intersection_line_and_circle, intersection_between_lines, \
    closest_point_on_segment, find_bisector_of_triangle, Area, Line
from ai.GameDomainObjects import Player

from ai.STA.Tactic.go_kick import GRAB_BALL_SPACING, GoKick

from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState



class GoalKeeper(Tactic):

    MOVING_BALL_VELOCITY = 50  # mm/s
    DANGER_BALL_VELOCITY = 600  # mm/s

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(),
                 penalty_kick=False, args: List[str]=None,):
        forbidden_area = [Area.pad(game_state.field.their_goal_area, KEEPOUT_DISTANCE_FROM_GOAL)]
        super().__init__(game_state, player, target, args, forbidden_areas=forbidden_area)

        self.current_state = self.defense
        self.next_state = self.defense

        self.target = Pose(self.game_state.field.our_goal, np.pi)  # Ignore target argument, always go for our goal

        self.go_kick_tactic = None # Used by clear
        self.last_intersection = None # For debug

        self.OFFSET_FROM_GOAL_LINE = Position(ROBOT_RADIUS + 10, 0)
        self.GOAL_LINE = self.game_state.field.our_goal_line

    def defense_dumb(self):
        dest_y = self.game_state.ball.position.y \
                 * self.game_state.goal_width / 2 / self.game_state.field.top
        position = self.game_state.field.our_goal - Position(ROBOT_RADIUS + 10, -dest_y)
        return MoveTo(Pose(position, np.pi))

    def defense(self):
        # Prepare to block the ball
        if self._is_ball_safe_to_kick() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        if self._ball_going_toward_goal():
            self.next_state = self.intercept
            return self.intercept()  # no time to loose

        circle_radius = self.game_state.field.goal_width / 2
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
                              end_speed=0)

        return MoveTo(Pose(self.game_state.field.our_goal, np.pi),
                      cruise_speed=3,
                      end_speed=0)

    def intercept(self):
        # Find the point where the ball will go
        if not self._ball_going_toward_goal() and not self.game_state.field.is_ball_in_our_goal_area():
            self.next_state = self.defense
        elif self.game_state.field.is_ball_in_our_goal_area() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        ball = self.game_state.ball
        where_ball_enter_goal = intersection_between_lines(self.GOAL_LINE.p1,
                                                           self.GOAL_LINE.p2,
                                                           ball.position,
                                                           ball.position + ball.velocity)

        # This is where the ball is going to enter the goal
        where_ball_enter_goal = closest_point_on_segment(where_ball_enter_goal, self.GOAL_LINE.p1, self.GOAL_LINE.p2)
        enter_goal_to_ball = Line(where_ball_enter_goal, ball.position)

        # The goalkeeper can not enter goal since there a line blocking vision
        end_segment = enter_goal_to_ball.direction * ROBOT_RADIUS + where_ball_enter_goal

        intersect_pts = closest_point_on_segment(self.player.position,
                                                 ball.position, end_segment)
        self.last_intersection = intersect_pts
        return MoveTo(Pose(intersect_pts, self.player.pose.orientation),  # It's a bit faster, to keep our orientation
                      cruise_speed=3,
                      end_speed=0,
                      ball_collision=False)

    def clear(self):
        # Move the ball to outside of the penality zone
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state,
                                         self.player,
                                         auto_update_target=True,
                                         go_behind_distance=1.2*GRAB_BALL_SPACING,
                                         forbidden_areas=self.forbidden_areas)  # make it easier
        if not self._is_ball_safe_to_kick():
            self.next_state = self.defense
            self.go_kick_tactic = None
            return Idle
        else:
            return self.go_kick_tactic.exec()

    def _ball_going_toward_goal(self):
        upper_angle = (self.game_state.ball.position - self.GOAL_LINE.p2).angle + 5 * np.pi / 180.0
        lower_angle = (self.game_state.ball.position - self.GOAL_LINE.p1).angle - 5 * np.pi / 180.0
        ball_speed = self.game_state.ball.velocity.norm
        return (ball_speed > self.DANGER_BALL_VELOCITY and self.game_state.ball.velocity.x > 0) or \
               (ball_speed > self.MOVING_BALL_VELOCITY and upper_angle <= self.game_state.ball.velocity.angle <= lower_angle)

    def _is_ball_safe_to_kick(self):
        # Since defender can not kick the ball while inside the goal there are position where the ball is unreachable
        # The goalee must leave the goal area and kick the ball
        goal_area = self.game_state.field.our_goal_area
        width = KEEPOUT_DISTANCE_FROM_GOAL + ROBOT_DIAMETER
        area_in_front_of_goal = Area.from_limits(goal_area.top, goal_area.bottom,
                                                 goal_area.left, goal_area.left - width)
        return self.game_state.field.is_ball_in_our_goal_area() or \
               area_in_front_of_goal.point_inside(self.game_state.ball.position) and self._no_enemy_around_ball()

    def _best_target_into_goal(self):
        if 0 < len(self.game_state.enemy_team.available_players):
            enemy_player_with_ball = player_with_ball(min_dist_from_ball=200, our_team=False)
            if enemy_player_with_ball is not None:
                if player_pointing_toward_segment(enemy_player_with_ball, self.GOAL_LINE):
                    ball = self.game_state.ball
                    where_ball_enter_goal = intersection_between_lines(self.GOAL_LINE.p1,
                                                                       self.GOAL_LINE.p2,
                                                                       ball.position,
                                                                       ball.position +
                                                                       Position(1000 * np.cos(enemy_player_with_ball.pose.orientation),
                                                                                1000 * np.sin(enemy_player_with_ball.pose.orientation)))
                    where_ball_enter_goal = closest_point_on_segment(where_ball_enter_goal,
                                                                     self.GOAL_LINE.p1,
                                                                     self.GOAL_LINE.p2)
                    return where_ball_enter_goal

        return find_bisector_of_triangle(self.game_state.ball.position,
                                         self.GOAL_LINE.p2,
                                         self.GOAL_LINE.p1)

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

    def _no_enemy_around_ball(self):
        closest = closest_players_to_point(self.game_state.ball_position, our_team=False)
        if len(closest) == 0:
            return True
        DANGEROUS_ENEMY_MIN_DISTANCE = 500
        return closest[0].distance > DANGEROUS_ENEMY_MIN_DISTANCE


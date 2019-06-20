# Under MIT licence, see LICENCE.txt

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory, GREEN
from Util.area import Area
from ai.Algorithm.evaluation_module import player_with_ball
from ai.STA.Tactic.goalkeeper import GoalKeeper

from typing import List

from Util import Pose, Position
from Util.ai_command import MoveTo, Idle, CmdBuilder
from Util.constant import ROBOT_RADIUS, KEEPOUT_DISTANCE_FROM_GOAL, ROBOT_DIAMETER, BALL_RADIUS
from Util.geometry import intersection_line_and_circle, intersection_between_lines, \
    closest_point_on_segment, find_bisector_of_triangle, Line, clamp
from ai.GameDomainObjects import Player
from ai.STA.Tactic.go_kick import GRAB_BALL_SPACING, GoKick
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


__author__ = 'RoboCupULaval'


class PenaltyGoalKeeper(GoalKeeper):
    """Same behavior as GoalKeeper, except the player must touch the goal line in defense and intercept"""


    MOVING_BALL_VELOCITY = 50  # mm/s
    DANGER_BALL_VELOCITY = 600  # mm/s
    DANGEROUS_ENEMY_MIN_DISTANCE = 500

    def __init__(self, game_state: GameState, player: Player, target: Pose = Pose(), args: List[str] = None, ):
        forbidden_area = [Area.pad(game_state.field.their_goal_area, KEEPOUT_DISTANCE_FROM_GOAL)]
        Tactic.__init__(self, game_state, player, target, args, forbidden_areas=forbidden_area)

        self.current_state = self.defense
        self.next_state = self.defense

        self.target = Pose(self.game_state.field.our_goal, np.pi)  # Ignore target argument, always go for our goal

        self.go_kick_tactic = None  # Used by clear
        self.last_intersection = None  # For debug

        self.OFFSET_FROM_GOAL_LINE = Position(ROBOT_RADIUS + 10, 0)
        self.GOAL_LINE = self.game_state.field.our_goal_line

        self.goal_to_solution_angle = None
        self.circle_radius = self.game_state.field.goal_width / 2
        self.circle_center = self.game_state.field.our_goal - self.OFFSET_FROM_GOAL_LINE

        self.min_angle_from_goal = np.arcsin(ROBOT_RADIUS / (self.game_state.field.goal_line.length / 2)) * 1.2

    def defense(self):
        if self._goalkeeper_stuck_behind_goal():
            self.next_state = self.move_out_from_behind_goal
            return self.next_state()

        # Prepare to block the ball
        if self._is_ball_safe_to_kick() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        if self._ball_going_toward_goal():
            self.next_state = self.intercept
            return self.intercept()  # no time to loose

        best_target_into_goal = self._best_target_into_goal()

        collisionless_goal_line = Line(self.GOAL_LINE.p1 - Position(0, ROBOT_RADIUS),
                                       self.GOAL_LINE.p2 + Position(0, ROBOT_RADIUS))
        best_target_into_goal = closest_point_on_segment(best_target_into_goal,
                                                         collisionless_goal_line.p1,
                                                         collisionless_goal_line.p2)

        best_target_into_goal.x -= ROBOT_RADIUS * 0.75  # We only need to touch the line

        return MoveTo(Pose(best_target_into_goal, np.pi),
                      cruise_speed=3,
                      end_speed=0)

    def intercept(self):
        if self._goalkeeper_stuck_behind_goal():
            self.next_state = self.move_out_from_behind_goal
            return self.next_state()

        if not self._ball_going_toward_goal() and not self.game_state.field.is_ball_in_our_goal_area():
            self.next_state = self.defense
        elif self.game_state.field.is_ball_in_our_goal_area() and self.game_state.ball.is_immobile():
            self.next_state = self.clear

        # Find the point where the ball will go
        ball = self.game_state.ball
        try:
            where_ball_enter_goal = intersection_between_lines(self.GOAL_LINE.p1,
                                                               self.GOAL_LINE.p2,
                                                               ball.position,
                                                               ball.position + ball.velocity)
        except ValueError: # In case of parallel lines
            self.next_state = self.defense
            return self.next_state()

        # This is where the ball is going to enter the goal
        collisionless_goal_line = Line(self.GOAL_LINE.p1 - Position(0, ROBOT_RADIUS),
                                       self.GOAL_LINE.p2 + Position(0, ROBOT_RADIUS))
        intersect_pts = closest_point_on_segment(where_ball_enter_goal,
                                                         collisionless_goal_line.p1,
                                                         collisionless_goal_line.p2)

        self.last_intersection = intersect_pts
        intersect_pts.x -= ROBOT_RADIUS * 0.75  # We only need to touch the line

        return MoveTo(Pose(intersect_pts, self.player.orientation),
                      cruise_speed=3,
                      end_speed=0)

    def clear(self):
        if self._goalkeeper_stuck_behind_goal():
            self.next_state = self.move_out_from_behind_goal
            return self.next_state()

        # Move the ball to outside of the penality zone
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state,
                                         self.player,
                                         auto_update_target=True,
                                         go_behind_distance=1.2 * GRAB_BALL_SPACING,
                                         forbidden_areas=self.forbidden_areas)  # make it easier
        if not self._is_ball_safe_to_kick():
            self.next_state = self.defense
            self.go_kick_tactic = None
            return Idle
        else:
            return self.go_kick_tactic.exec()

    def _is_ball_safe_to_kick(self):
        penalty_line_x = self.game_state.field.our_goal_area.left
        ball = self.game_state.ball_position
        # The referee is suppose to place the ball at the penalty line.
        # However they are never super precise, so we will not react to if the ball is a bit inside our goal.
        return self.game_state.field.is_ball_in_our_goal_area() and penalty_line_x + BALL_RADIUS * 12 < ball.x


    def _best_target_into_goal(self):
        if 0 < len(self.game_state.enemy_team.available_players):
            enemy_player_with_ball = player_with_ball(min_dist_from_ball=4 * ROBOT_RADIUS, our_team=False)
            if enemy_player_with_ball is not None:
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
            return [DebugCommandFactory().line(self.game_state.ball.position,
                                               self._best_target_into_goal(),
                                               color=GREEN,
                                               timeout=0.1),
                    DebugCommandFactory().line(self.game_state.ball_position, self.field.our_goal)
                    ]

        elif self.current_state == self.intercept and self.last_intersection is not None:
            return DebugCommandFactory().line(self.game_state.ball.position,
                                              self.last_intersection,
                                              timeout=0.1)
        else:
            return []
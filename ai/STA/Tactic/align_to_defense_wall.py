# Under MIT licence, see LICENCE.txt
import time
from math import tan
from typing import List, Optional

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory
from Util import Pose, Position
from Util.geometry import perpendicular, normalize, find_bisector_of_triangle, angle_between_three_points, Line, \
    intersection_line_and_circle

from Util.constant import BALL_RADIUS, ROBOT_RADIUS, ROBOT_DIAMETER, KEEPOUT_DISTANCE_FROM_BALL
from Util.role import Role
from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.GameDomainObjects import Player
from Util.ai_command import Idle, CmdBuilder, MoveTo
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2

GAP_IN_WALL = 40  # in mm, distance that prevent robots from touching each other
FETCH_BALL_ZONE_RADIUS = 1000  # in mm, circle around the wall's robot, where it can go kick the ball

class AlignToDefenseWall(Tactic):
    def __init__(self, game_state: GameState,
                 player: Player,
                 args: Optional[List[str]]=None,
                 robots_in_formation: Optional[List[Player]]=None,
                 object_to_block=None,
                 stay_away_from_ball=False,
                 cruise_speed=3):
        super().__init__(game_state, player, args=args)
        if object_to_block is None:
            object_to_block = GameState().ball
        self.object_to_block = object_to_block
        if robots_in_formation is None:
            self.robots_in_formation = [player]
        else:
            self.robots_in_formation = robots_in_formation
        assert isinstance(self.robots_in_formation[0], Player)

        self.cruise_speed = cruise_speed
        self.stay_away_from_ball = stay_away_from_ball
        self.go_kick_tactic = None
        self.player_number_in_formation = None
        self.wall_segment = None

        # Used for debug_cmd() visualization
        self.bisect_inter = None
        self.center_formation = None

        self.init_players_in_formation()

        self.current_state = self.main_state
        self.next_state = self.main_state

    def init_players_in_formation(self):
        self.player_number_in_formation = self.robots_in_formation.index(self.player)

    def compute_wall_segment(self):
        """
            We compute the position where the wall's robot can block the field of view of opposing robot with the ball.
            The field of view is defined as the triangle created by the ball and the goal_line extremities.
        """

        nb_robots = len(self.robots_in_formation)
        wall_segment_length = nb_robots * ROBOT_DIAMETER + GAP_IN_WALL * (nb_robots - 1)

        goal_line = self.game_state.field.our_goal_line
        bisection_angle = angle_between_three_points(goal_line.p2, self.object_to_block.position, goal_line.p1)

        # We calculate the farthest distance from the object which completely block its FOV of the goal
        object_to_center_formation_dist = wall_segment_length / tan(bisection_angle)

        self.bisect_inter = find_bisector_of_triangle(self.object_to_block.position, goal_line.p1, goal_line.p2)
        vec_object_to_goal_line_bisect = self.bisect_inter - self.object_to_block.position

        # The penalty zone used to be a circle and thus really easy to handle, but now it's a rectangle...
        # It easier to first create the smallest circle that fit the rectangle.
        min_radius_over_penality_zone = ROBOT_RADIUS + (self.game_state.field.our_goal_area.upper_left - self.game_state.field.our_goal).norm
        object_to_block_to_center_formation_dist = min(vec_object_to_goal_line_bisect.norm - min_radius_over_penality_zone,
                                                       object_to_center_formation_dist)

        self.center_formation = object_to_block_to_center_formation_dist * normalize(vec_object_to_goal_line_bisect) + self.object_to_block.position

        if self.stay_away_from_ball:
            if (self.game_state.ball_position - self.center_formation).norm < KEEPOUT_DISTANCE_FROM_BALL:
                self.center_formation = self._closest_point_away_from_ball()

        half_wall_segment = 0.5 * wall_segment_length * perpendicular(normalize(vec_object_to_goal_line_bisect))
        self.wall_segment = Line(self.center_formation + half_wall_segment,
                                 self.center_formation - half_wall_segment)

    def position_on_wall_segment(self):
        idx = self.player_number_in_formation
        length = ROBOT_RADIUS + idx * (ROBOT_DIAMETER + GAP_IN_WALL)
        return self.wall_segment.p1 + self.wall_segment.direction * length

    def debug_cmd(self):
        if self.wall_segment is None or self.player_number_in_formation != 0:
            return []
        return [DebugCommandFactory().line(self.wall_segment.p1,
                                           self.wall_segment.p2,
                                           timeout=0.1),
                DebugCommandFactory().line(self.center_formation,
                                           self.bisect_inter,
                                           timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                           self.game_state.field.our_goal_line.p1,
                                           timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                           self.game_state.field.our_goal_line.p2,
                                           timeout=0.1)
                ]

    def main_state(self):
        self.compute_wall_segment()
        if self.game_state.field.is_ball_in_our_goal_area():
            return Idle  # We must not block the goalkeeper
        elif self._should_ball_be_kick_by_wall() \
                and self._is_closest_not_goaler(self.player) \
                and self._no_enemy_around_ball():
            self.next_state = self.go_kick
        dest = self.position_on_wall_segment()
        dest_orientation = (self.object_to_block.position - dest).angle
        return MoveTo(Pose(dest,
                           dest_orientation), cruise_speed=self.cruise_speed)

    def go_kick(self):
        self.compute_wall_segment()
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state, self.player, target=self.game_state.field.their_goal_pose)

        if not self._should_ball_be_kick_by_wall() \
                or self.game_state.field.is_ball_in_our_goal_area() \
                or not self._is_closest_not_goaler(self.player) \
                or not self._no_enemy_around_ball():
            self.go_kick_tactic = None
            self.next_state = self.main_state
            return Idle
        else:
            return self.go_kick_tactic.exec()

    def _should_ball_be_kick_by_wall(self):
        return not self.stay_away_from_ball and \
               (self.position_on_wall_segment() - self.game_state.ball.position).norm < FETCH_BALL_ZONE_RADIUS

    def _is_closest_not_goaler(self, player):
        closest_players = closest_players_to_point(GameState().ball_position, our_team=True)
        if player == closest_players[0].player:
            return True
        return closest_players[0].player == self.game_state.get_player_by_role(Role.GOALKEEPER) \
               and player == closest_players[1].player

    def _closest_point_away_from_ball(self):
        inters = intersection_line_and_circle(self.game_state.ball_position, KEEPOUT_DISTANCE_FROM_BALL,
                                              self.object_to_block.position, self.bisect_inter)
        if len(inters) == 1:
            return inters[0]
        if (inters[0] - self.bisect_inter).norm < (inters[1] - self.bisect_inter).norm:
            return inters[0]
        else:
            return inters[1]

    def _no_enemy_around_ball(self):
        DANGEROUS_ENEMY_MIN_DISTANCE = 500
        ball_position = self.game_state.ball_position
        for enemy in self.game_state.enemy_team.available_players.values():
            if (enemy.position - ball_position).norm < DANGEROUS_ENEMY_MIN_DISTANCE:
                return False
        return True




# Under MIT licence, see LICENCE.txt
import time
from math import tan
from typing import List, Optional

import numpy as np

from Debug.debug_command_factory import DebugCommandFactory
from Util import Pose, Position
from Util.geometry import perpendicular, normalize, find_bisector_of_triangle, angle_between_three_points

from Util.constant import BALL_RADIUS, ROBOT_RADIUS, ROBOT_DIAMETER
from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.GameDomainObjects import Player
from Util.ai_command import Idle, CmdBuilder, MoveTo
from ai.GameDomainObjects.field import Line
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2


GAB_IN_WALL = 40  # in mm, distance that prevent robots from touching each other
FETCH_BALL_ZONE_RADIUS = 1000  # in mm, circle around the formation center, where the wall member can go kick the ball

class AlignToDefenseWall(Tactic):
    def __init__(self, game_state: GameState,
                 player: Player,
                 args: Optional[List[str]]=None,
                 robots_in_formation: Optional[List[Player]]=None,
                 auto_pick=False):
        super().__init__(game_state, player, args=args)

        if robots_in_formation is None:
            self.robots_in_formation = [player]
        else:
            self.robots_in_formation = robots_in_formation
        assert isinstance(self.robots_in_formation[0], Player)

        self.last_time = time.time()
        self.auto_pick = auto_pick

        self.robots = self.robots_in_formation.copy()  # why

        self.field_goal_radius = self.game_state.const["FIELD_GOAL_RADIUS"]
        self.field_goal_segment = self.game_state.const["FIELD_GOAL_SEGMENT"]
        self.keep_out_distance = self.field_goal_radius * 1.5
        self.goal_width = self.game_state.const["FIELD_GOAL_WIDTH"]
        self.goal_middle = Position(self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
        self.position_middle_formation = Position(0, 0)
        self.positions_in_formations = []
        self.vec_ball_2_goal = Position(1, 0)
        self.vec_perp_of_ball_2_goal = Position(0, 1)
        self.player_number_in_formation = None
        self.nb_robots = 0

        # I use this
        self.go_kick_tactic = None

        # Used for debug_cmd visualization
        self.wall_segment = None
        self.bisect_inter = None
        self.center_formation = None

        self.init_players_in_formation()

        self.current_state = self.main_state
        self.next_state = self.main_state

    def init_players_in_formation(self):
        self.player_number_in_formation = None
        self.robots_in_formation = self.robots

        for idx, player in enumerate(self.robots_in_formation):
            if self.player == player:
                self.player_number_in_formation = idx
                break
        else:
            raise RuntimeError("The current player is not in the formation")

        self.nb_robots = len(self.robots_in_formation)

    def define_wall_segment(self):
        nb_robots = len(self.robots_in_formation)
        wall_segment_length = nb_robots * ROBOT_DIAMETER + GAB_IN_WALL * (nb_robots - 1)

        ball_position = self.game_state.ball_position
        goal_line = self.game_state.field.goal_line
        bisection_angle = angle_between_three_points(goal_line.p2, ball_position, goal_line.p1)

        ball_to_center_formation_dist = wall_segment_length / tan(bisection_angle)

        self.bisect_inter = find_bisector_of_triangle(ball_position, goal_line.p1, goal_line.p2)
        vec_ball_to_goal_line_bisect = self.bisect_inter - ball_position

        # The penality zone used to be a circle and thus really easy to handle, but now it's a rectangle...
        # It easier to first create the smallest circle that fit the rectangle.
        min_radius_over_penality_zone = ROBOT_RADIUS + (self.game_state.field.our_goal_area.a - self.game_state.field.our_goal).norm
        ball_to_center_formation_dist = min(vec_ball_to_goal_line_bisect.norm - min_radius_over_penality_zone,
                                            ball_to_center_formation_dist)

        self.center_formation = ball_to_center_formation_dist * normalize(vec_ball_to_goal_line_bisect) + ball_position

        half_wall_segment = 0.5 * wall_segment_length * perpendicular(normalize(vec_ball_to_goal_line_bisect))
        self.wall_segment = Line(self.center_formation + half_wall_segment,
                                 self.center_formation - half_wall_segment)


    def position_on_wall_segment(self):
        idx = self.player_number_in_formation
        length = ROBOT_RADIUS + idx * (ROBOT_DIAMETER + GAB_IN_WALL)
        return self.wall_segment.p1 + self.wall_segment.normalize * length

    def debug_cmd(self):
        if self.wall_segment is None:
            return []
        return [DebugCommandFactory().line(self.wall_segment.p1,
                                          self.wall_segment.p2,
                                            timeout=0.1),
                DebugCommandFactory().line(self.center_formation,
                                           self.bisect_inter,
                                           timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                           self.game_state.field.goal_line.p1,
                                           timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                           self.game_state.field.goal_line.p2,
                                           timeout=0.1)
                ]

    def define_center_of_formation(self):
        """
        on calcul la position du points qui intersecte le segment de droite allant de la ball jusqu'au but et le cercle
        de rayon self.keep_out_distance.

        Ensuite on crée triangle isocèle qui à comme base le segment de droite composé de la projection du segment
        reliant les deux coins des buts sur le vecteur perpendiculaire au vecteur ball_goal.

        On calcul ensuite l'emplacement d'un point situé sur le segment de droite appatenant au tirangle
        qui permetra de bloquer le champ de vision du robot ennemi. Ce point est calculé en ayant recourt aux
        propriété des triangles semblables.
        """
        pass

    def main_state(self):
        self.define_wall_segment()
        if self.game_state.field.is_ball_in_our_goal():
            return Idle  # We need to not block the goalkeeper
        elif self._should_ball_be_kick_by_wall() and self._is_closest(self.player):
            self.next_state = self.go_kick
        dest = self.position_on_wall_segment()
        dest_orientation = (self.game_state.ball_position - dest).angle
        return MoveTo(Pose(dest,
                           dest_orientation))

    def go_kick(self):
        self.define_wall_segment()
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state, self.player, target=self.game_state.field.their_goal_pose)

        if not self._should_ball_be_kick_by_wall() or self.game_state.field.is_ball_in_our_goal():
            self.go_kick_tactic = None
            self.next_state = self.main_state
            return Idle
        else:
            return self.go_kick_tactic.exec()

    def _should_ball_be_kick_by_wall(self):
        return (self.center_formation - self.game_state.ball.position).norm < FETCH_BALL_ZONE_RADIUS

    def _is_closest(self, player):
        return player == closest_players_to_point(GameState().ball_position, our_team=True)[0].player


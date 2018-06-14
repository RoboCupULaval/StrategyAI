# Under MIT licence, see LICENCE.txt
from math import atan, pi, cos, sin
from typing import List, Optional

from Debug.debug_command_factory import DebugCommandFactory, RED
from Util import Pose, Position
from Util.ai_command import Idle, MoveTo
from Util.constant import ROBOT_RADIUS, KEEPOUT_DISTANCE_FROM_BALL
from Util.geometry import normalize, find_bisector_of_triangle, angle_between_three_points
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

GAP_ANGLE = 10 * pi / 180  # in rad, distance that prevent robots from touching each other


class AlignAroundTheBall(Tactic):
    def __init__(self, game_state: GameState,
                 player: Player,
                 target: Pose = Pose(),
                 args: Optional[List[str]] = None,
                 robots_in_formation: Optional[List[Player]] = None):
        super().__init__(game_state, player, args=args)
        if robots_in_formation is None:
            self.robots_in_formation = [player]
        else:
            self.robots_in_formation = robots_in_formation
        assert isinstance(self.robots_in_formation[0], Player)

        self.player_number_in_formation = None

        self.init_players_in_formation()

        self.current_state = self.main_state
        self.next_state = self.main_state

        self.dist_from_ball = KEEPOUT_DISTANCE_FROM_BALL * 1.1

    def init_players_in_formation(self):
        self.player_number_in_formation = self.robots_in_formation.index(self.player)

    def compute_wall_arc(self):
        nb_robots = len(self.robots_in_formation)

        # Angle d'un robot sur le cercle de rayon self.dist_from_ball
        self.robot_angle = 2 * atan(ROBOT_RADIUS / self.dist_from_ball)

        # Angle totale couvert par le wall
        self.wall_angle = nb_robots * self.robot_angle + GAP_ANGLE * (nb_robots - 1)

        goal_line = self.game_state.field.goal_line

        angle_to_cover = angle_between_three_points(goal_line.p1, self.game_state.ball_position, goal_line.p2)

        self.center_of_goal = find_bisector_of_triangle(self.game_state.ball_position, goal_line.p1, goal_line.p2)
        vec_ball_to_center_of_goal = self.center_of_goal - self.game_state.ball_position

        # Centre de la formation sur le cercle de rayon self.dist_from_ball
        self.center_formation = self.dist_from_ball * normalize(
            vec_ball_to_center_of_goal) + self.game_state.ball_position

        # J'ajoute robot_angle / 2, sinon, avec 1 seul robot, il ne se positionne pas dans le centre de la formation
        self.first_robot_angle = vec_ball_to_center_of_goal.angle - self.wall_angle / 2 + self.robot_angle / 2

        self.first_robot_position = Position(cos(self.first_robot_angle),
                                             sin(self.first_robot_angle)) * self.dist_from_ball + \
                                    self.game_state.ball_position

        self.last_robot_angle = self.first_robot_angle + self.wall_angle


    def angle_on_wall_arc(self):
        idx = self.player_number_in_formation
        angle_from_p1 = self.first_robot_angle + idx * (self.robot_angle + GAP_ANGLE)  # premier point sur l'arc
        return angle_from_p1

    def debug_cmd(self):
        if self.player_number_in_formation != 0:
            return []
        return [
                # DebugCommandFactory().line(self.center_formation,
                #                            self.center_of_goal,
                #                            color=RED,
                #                            timeout=0.1),
                # DebugCommandFactory().line(self.game_state.ball_position,
                #                            self.game_state.field.goal_line.p1,
                #                            timeout=0.1),
                # DebugCommandFactory().line(self.game_state.ball_position,
                #                            self.game_state.field.goal_line.p2,
                #                            timeout=0.1),
                # DebugCommandFactory().circle(self.game_state.ball_position, self.dist_from_ball, is_fill=False,
                #                              timeout=0.1),
                # DebugCommandFactory().circle(self.first_robot_position, 100,
                #                              color=RED,
                #                              is_fill=True,
                #                              timeout=0.1),
                # DebugCommandFactory().circle(self.last_robot_position, 100,
                #                              color=RED,
                #                              is_fill=True,
                #                              timeout=0.1)
                ]

    def main_state(self):
        self.compute_wall_arc()
        if self.game_state.field.is_ball_in_our_goal_area():
            return Idle  # We must not block the goalkeeper
        angle = self.angle_on_wall_arc()
        dest = Position(cos(angle), sin(angle)) * self.dist_from_ball + self.game_state.ball_position
        dest_orientation = (self.game_state.ball_position - dest).angle
        return MoveTo(Pose(dest, dest_orientation), cruise_speed=0.8)

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

GAP_ANGLE = pi / 60  # in rad, distance that prevent robots from touching each other


class AlignAroundTheBall(Tactic):
    def __init__(self, game_state: GameState,
                 player: Player,
                 target: Pose=Pose(),
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

    def init_players_in_formation(self):
        self.player_number_in_formation = self.robots_in_formation.index(self.player)

    def compute_wall_arc(self):
        nb_robots = len(self.robots_in_formation)

        # Angle d'un robot sur le cercle de rayon KEEPOUT_DISTANCE_FROM_BALL
        self.angle_robot = 2 * atan(ROBOT_RADIUS / KEEPOUT_DISTANCE_FROM_BALL)

        # Angle totale couvert par le wall
        self.wall_angle = nb_robots * self.angle_robot + GAP_ANGLE * (nb_robots - 1)

        goal_line = self.game_state.field.goal_line

        # Angle a couvrir
        angle_to_cover = angle_between_three_points(goal_line.p1, self.game_state.ball_position, goal_line.p2)

        self.center_of_goal = find_bisector_of_triangle(self.game_state.ball_position, goal_line.p1, goal_line.p2)
        vec_ball_to_center_of_goal = self.center_of_goal - self.game_state.ball_position

        # Centre de la formation sur le cercle de rayon KEEPOUT_DISTANCE_FROM_BALL
        self.center_formation = KEEPOUT_DISTANCE_FROM_BALL * normalize(vec_ball_to_center_of_goal) + self.game_state.ball_position


        print("wall angle : {}".format(self.wall_angle))
        print("angle to cover : {}".format(angle_to_cover))

        self.angle_to_first_robot = vec_ball_to_center_of_goal.angle - self.wall_angle / 2

        print("vec_ball_to_center_of_goal angle : {}".format(vec_ball_to_center_of_goal.angle))
        print("angle to first robot : {}".format(self.angle_to_first_robot))

        self.first_robot_position = Position(cos(self.angle_to_first_robot) * KEEPOUT_DISTANCE_FROM_BALL, sin(self.angle_to_first_robot) * KEEPOUT_DISTANCE_FROM_BALL) + \
                                    self.game_state.ball_position

        print("first robot position : {}".format(self.first_robot_position))
        print("ball position : {}".format(self.game_state.ball_position))

    def position_on_wall_segment(self):
        idx = self.player_number_in_formation
        angle_from_p1 = ROBOT_RADIUS + idx * (self.angle_robot + GAP_ANGLE)  # premier point sur l'arc
        return angle_from_p1

    def debug_cmd(self):
        if self.player_number_in_formation != 0:
            return []
        return [DebugCommandFactory().line(self.center_formation,
                                           self.center_of_goal,
                                           color=RED,
                                           timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                           self.game_state.field.goal_line.p1,
                                           timeout=0.1),
                DebugCommandFactory().line(self.game_state.ball_position,
                                           self.game_state.field.goal_line.p2,
                                           timeout=0.1),
                DebugCommandFactory().circle(self.game_state.ball_position, KEEPOUT_DISTANCE_FROM_BALL, is_fill=False,
                                             timeout=0.1),
                DebugCommandFactory().circle(self.first_robot_position, 100,
                                             color=RED,
                                             is_fill=True,
                                             timeout=0.1),
                ]

    def main_state(self):
        self.compute_wall_arc()
        if self.game_state.field.is_ball_in_our_goal_area():
            return Idle  # We must not block the goalkeeper
        angle = self.position_on_wall_segment()
        dest = Position(cos(angle) + self.game_state.ball_position.x, sin(angle) + self.game_state.ball_position.y)
        dest_orientation = (self.game_state.ball_position - dest).angle
        return MoveTo(Pose(dest, dest_orientation))

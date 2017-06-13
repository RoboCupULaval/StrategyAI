# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.STA.Tactic.Tactic import Tactic
from ai.states.game_state import GameState
from RULEngine.Util.constant import TeamColor

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.0


class AllignToDefenseWall(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, number_of_robots: int=0, robot_formation_number: int=0,
                 args: List[str]=None):
        Tactic.__init__(self, game_state, player, args=args)
        self.current_state = self.go_allign
        self.next_state = self.go_allign
        self.game_state = game_state
        self.last_time = time.time()
        self.number_of_robots = number_of_robots
        self.player = player
        self.robot_formation_number = robot_formation_number
        self.field_goal_radius = self.game_state.const["FIELD_GOAL_RADIUS"]
        self.field_goal_segment = self.game_state.const["FIELD_GOAL_SEGMENT"]
        self.keep_out_distance = self.field_goal_radius + self.field_goal_segment
        self.goal_width = self.game_state.field.constant["GOAL_WIDTH"]
        if self.player.team.team_color is TeamColor.BLUE:
            self.goal_middle = Position(-self.game_state.field.constant["FIELD_X_RIGHT"], 0)
        else:
            self.goal_middle = Position(self.game_state.field.constant["FIELD_X_RIGHT"], 0)

    def go_allign(self):
        """
        on calcul la position du points qui intersecte le segment de droite allant de la ball jusqu'au but et le cercle
        de rayon self.keep_out_distance.

        Ensuite on crée triangle isocèle qui à comme base le segment de droite composé de la projection du segment
        reliant les deux coins des buts sur le vecteur perpendiculaire au vecteur ball_goal.

        On calcul ensuite l'emplacement d'un point situé sur le segment de droite appatenant au tirangle
        qui permetra de bloquer le champ de vision du robot ennemi. Ce point est calculé en ayant recourt aux
        propriété des triangles semblables.
        """


        ball_position = self.game_state.get_ball_position()
        vec_ball_2_goal = self.goal_middle - ball_position
        """
        respecte la règle de la main droite et pointe toujours vers le coin suppérieur du but si on est à gauche du 
        terrain et l'inverse si on est à droite du terrain
        """
        vec_perp_of_ball_2_goal = vec_ball_2_goal.perpendicular()
        vec_ball_2_goal_top = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0) - ball_position
        vec_ball_2_goal_bottom = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0) - ball_position
        vec_bottom_goal_2_to_goal = Position(self.goal_width * 2.0, 0)

        vec_triangle_base = np.multiply(np.dot(vec_perp_of_ball_2_goal, vec_bottom_goal_2_to_goal),
                                        vec_perp_of_ball_2_goal)
        if vec_ball_2_goal_top.norm() < vec_ball_2_goal_bottom.norm():
            lower_triangle_corner = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0) - vec_triangle_base
            upper_tirangle_corner = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0)
        else:
            upper_tirangle_corner = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0) + vec_triangle_base
            lower_triangle_corner = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0)
        vec_ball_2_limit_circle = (vec_ball_2_goal.norm() - self.keep_out_distance) * \
                                  (self.goal_middle - ball_position).normalize()




















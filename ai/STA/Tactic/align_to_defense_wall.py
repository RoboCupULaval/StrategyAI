# Under MIT licence, see LICENCE.txt
import time
from typing import List, Optional

import numpy as np

from Util import Pose, Position
from Util.geometry import perpendicular, normalize

from Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.GameDomainObjects import Player
from Util.ai_command import Idle, CmdBuilder, MoveTo
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.0

DEAD_ZONE = 30  # We lost the true value, but who cares


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

        self.robots = self.robots_in_formation.copy() # why

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
        self.number_of_robots = 0

        self.init_players_in_formation()

        self.next_state = self.main_state

    def init_players_in_formation(self):
        self.player_number_in_formation = None
        self.robots_in_formation = self.robots

        for idx, player in enumerate(self.robots_in_formation):
            if self.player == player:
                self.player_number_in_formation = idx
                break

        if self.player_number_in_formation is None:
            raise RuntimeError("The current player is not in the formation")

        self.number_of_robots = len(self.robots_in_formation)


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

        self.ball_position = self.game_state.ball_position
        self.vec_ball_2_goal = self.goal_middle - self.ball_position
        """
        respecte la règle de la main droite et pointe toujours vers le coin suppérieur du but si on est à gauche du 
        terrain et l'inverse si on est à droite du terrain
        """
        self.vec_perp_of_ball_2_goal = -perpendicular(self.vec_ball_2_goal)
        # vec_ball_2_goal_top = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0) - ball_position
        # vec_ball_2_goal_bottom = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0) - ball_position
        vec_bottom_goal_2_to_top_goal = Position(self.goal_width, 0)

        vec_triangle_base = np.multiply(np.dot(self.vec_perp_of_ball_2_goal, vec_bottom_goal_2_to_top_goal),
                                        self.vec_perp_of_ball_2_goal)
        # if vec_ball_2_goal_top.norm < vec_ball_2_goal_bottom.norm:
        #     lower_triangle_corner = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0) - vec_triangle_base
        #     upper_tirangle_corner = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0)
        # else:
        #     upper_tirangle_corner = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0) + vec_triangle_base
        #     lower_triangle_corner = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0)
        vec_ball_2_limit_circle = (self.vec_ball_2_goal.norm - self.keep_out_distance) * \
                                  normalize(self.goal_middle - self.ball_position)
        #if self.number_of_robots * 1.8 * ROBOT_RADIUS > vec_triangle_base.norm:
        if True:
            self.position_middle_formation = self.ball_position + vec_ball_2_limit_circle * 0.8
        else:
            self.position_middle_formation = self.ball_position + \
                                             normalize(vec_ball_2_limit_circle) * \
                                             (self.number_of_robots * 1.8 * ROBOT_RADIUS / vec_triangle_base.norm)

    def compute_positions_in_formation(self):
        if self.number_of_robots == 1:
            self.positions_in_formations = [self.position_middle_formation]
        elif self.number_of_robots == 2:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_1 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1

            self.positions_in_formations = [position_0, position_1]

        elif self.number_of_robots == 3:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * 2. * ROBOT_RADIUS * 1.1 + \
                         normalize(self.vec_ball_2_goal) * ROBOT_RADIUS * 0.9
            position_1 = self.position_middle_formation - normalize(self.vec_ball_2_goal) * ROBOT_RADIUS * 1.1
            position_2 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * 2. * ROBOT_RADIUS * 1.1 + \
                         normalize(self.vec_ball_2_goal) * ROBOT_RADIUS * 0.9

            self.positions_in_formations = [position_0, position_1, position_2]

        elif self.number_of_robots == 4:
            local_middle_of_formation = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS /2.
            position_0 = local_middle_of_formation + self.vec_perp_of_ball_2_goal * 3. * ROBOT_RADIUS * 1.1
            position_1 = local_middle_of_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_2 = local_middle_of_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_3 = local_middle_of_formation - self.vec_perp_of_ball_2_goal * 3. * ROBOT_RADIUS * 1.1

            self.positions_in_formations = [position_0, position_1, position_2, position_3]

        elif self.number_of_robots == 5:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * 3. * ROBOT_RADIUS * 1.1 + \
                         normalize(self.vec_ball_2_goal) * 3. * ROBOT_RADIUS * 0.9
            position_1 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1 + \
                         normalize(self.vec_ball_2_goal) * ROBOT_RADIUS * 0.9
            position_2 = self.position_middle_formation - normalize(self.vec_ball_2_goal) * ROBOT_RADIUS * 1.1
            position_3 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1 + \
                         normalize(self.vec_ball_2_goal) * ROBOT_RADIUS * 0.9
            position_4 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * 3 * ROBOT_RADIUS * 1.1 + \
                         normalize(self.vec_ball_2_goal) * 3. * ROBOT_RADIUS * 0.9

            self.positions_in_formations = [position_0, position_1, position_2, position_3, position_4]
        else:
            raise RuntimeError("Usupported number of player in formation {}".format(self.number_of_robots))
        # print(self.positions_in_formations)

    def main_state(self):
        self.define_center_of_formation()
        self.compute_positions_in_formation()
        # print(self.player_number_in_formation)
        # for idx, player in enumerate(self.robots_in_formation):
        #     if not self.is_not_one_of_the_closests(player):
        #         self.init_players_in_formation()
        #         self.define_center_of_formation()
        #         self.compute_positions_in_formation()
        #         break
        # print(self.robots_in_formation)
        # print(self.player_number_in_formation)
        # print(self.player.id)
        if self.check_success():
            self.status_flag = Flags.SUCCESS
            return Idle
        else:
            destination_orientation = (self.ball_position -
                                       self.positions_in_formations[self.player_number_in_formation]).angle
            return MoveTo(Pose(self.positions_in_formations[self.player_number_in_formation],
                               destination_orientation))

    def check_success(self):
        player_position = self.player.pose.position
        distance = (player_position - self.target.position).norm
        if distance < DEAD_ZONE:
            return True
        return False

    @staticmethod
    def is_closest(robots, player):
        if player == closest_players_to_point(GameState().ball_position, True, robots)[0].player:
            return True
        return False

    @staticmethod
    def is_second_closest(robots, player):
        if player == closest_players_to_point(GameState().ball_position, True, robots)[1].player:
            return True
        return False

    def is_not_closest(self, player):
        return not(self.is_closest(self.robots, player))

    def is_not_one_of_the_closests(self, player):
        return not(self.is_closest(self.robots, player) or self.is_second_closest(self.robots, player))

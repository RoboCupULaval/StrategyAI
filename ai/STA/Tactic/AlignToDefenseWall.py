# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS, TeamColor
from RULEngine.Util.geometry import get_angle
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState
from ai.STA.Action.Idle import Idle

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.0


class AllignToDefenseWall(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, robots_in_formation: List[OurPlayer],
                 args: List[str]=None):
        assert isinstance(robots_in_formation[0], OurPlayer)
        Tactic.__init__(self, game_state, player, args=args)
        self.current_state = self.define_center_of_formation
        self.next_state = self.define_center_of_formation
        self.game_state = game_state
        self.last_time = time.time()
        self.robots_in_formation = robots_in_formation

        self.player = player
        self.field_goal_radius = self.game_state.const["FIELD_GOAL_RADIUS"]
        self.field_goal_segment = self.game_state.const["FIELD_GOAL_SEGMENT"]
        self.keep_out_distance = self.field_goal_radius + np.divide(self.field_goal_segment, 2.)
        self.goal_width = self.game_state.const["GOAL_WIDTH"]
        if self.player.team.team_color is TeamColor.BLUE:
            self.goal_middle = Position(-self.game_state.field.constant["FIELD_X_RIGHT"], 0)
        else:
            self.goal_middle = Position(self.game_state.field.constant["FIELD_X_RIGHT"], 0)
        self.position_middle_formation = Position(0, 0)
        self.positions_in_formations = []
        self.vec_ball_2_goal = Position(1, 0)
        self.vec_perp_of_ball_2_goal = Position(0, 1)
        self.player_number_in_formation = None
        if len(self.robots_in_formation) == 0:
            self.next_state = self.halt
            self.number_of_robots = 0
        else:
            self.number_of_robots = len(self.robots_in_formation)
        for idx, player in enumerate(self.robots_in_formation):
            print(player is self.player)
            if player is self.player:
                self.player_number_in_formation = idx
                print(self.player_number_in_formation)
        if self.player_number_in_formation is None:
            self.player_number_in_formation = 0
            self.next_state = self.halt

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


        self.ball_position = self.game_state.get_ball_position()
        self.vec_ball_2_goal = self.goal_middle - self.ball_position
        """
        respecte la règle de la main droite et pointe toujours vers le coin suppérieur du but si on est à gauche du 
        terrain et l'inverse si on est à droite du terrain
        """
        self.vec_perp_of_ball_2_goal = self.vec_ball_2_goal.perpendicular()
        # vec_ball_2_goal_top = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0) - ball_position
        # vec_ball_2_goal_bottom = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0) - ball_position
        vec_bottom_goal_2_to_top_goal = Position(self.goal_width, 0)

        vec_triangle_base = np.multiply(np.dot(self.vec_perp_of_ball_2_goal, vec_bottom_goal_2_to_top_goal),
                                        self.vec_perp_of_ball_2_goal)
        # if vec_ball_2_goal_top.norm() < vec_ball_2_goal_bottom.norm():
        #     lower_triangle_corner = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0) - vec_triangle_base
        #     upper_tirangle_corner = self.goal_middle + np.divide(Position(self.goal_width, 0), 2.0)
        # else:
        #     upper_tirangle_corner = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0) + vec_triangle_base
        #     lower_triangle_corner = self.goal_middle - np.divide(Position(self.goal_width, 0), 2.0)
        vec_ball_2_limit_circle = (self.vec_ball_2_goal.norm() - self.keep_out_distance) * \
                                  (self.goal_middle - self.ball_position).normalized()
        #if self.number_of_robots * 1.8 * ROBOT_RADIUS > vec_triangle_base.norm():
        if True:
            self.position_middle_formation = self.ball_position + vec_ball_2_limit_circle * 0.8
        else:
            self.position_middle_formation = self.ball_position + \
                                            vec_ball_2_limit_circle.normalized() * \
                                            (self.number_of_robots * 1.8 * ROBOT_RADIUS / vec_triangle_base.norm())

    def compute_positions_in_formation(self):
        if self.number_of_robots == 1:
            self.positions_in_formations = [self.position_middle_formation]
        elif self.number_of_robots == 2:
            print(self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 10)
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1
            position_1 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1

            self.positions_in_formations = [position_0, position_1]

        elif self.number_of_robots == 3:
            position_0 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * 2. * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9
            position_1 = self.position_middle_formation - self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 1.1
            position_2 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * 2. * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9

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
                         self.vec_ball_2_goal.normalized() * 3. * ROBOT_RADIUS * 0.9
            position_1 = self.position_middle_formation + self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9
            position_2 = self.position_middle_formation - self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 1.1
            position_3 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * ROBOT_RADIUS * 0.9
            position_4 = self.position_middle_formation - self.vec_perp_of_ball_2_goal * 3 * ROBOT_RADIUS * 1.1 + \
                         self.vec_ball_2_goal.normalized() * 3. * ROBOT_RADIUS * 0.9

            self.positions_in_formations = [position_0, position_1, position_2, position_3, position_4]

    def exec(self):
        self.define_center_of_formation()
        self.compute_positions_in_formation()
        if self.check_success():
            return self.halt
        else:
            destination_orientation = get_angle(self.positions_in_formations[self.player_number_in_formation],
                                                self.ball_position)
            return GoToPositionPathfinder(self.game_state, self.player,
                                          Pose(self.positions_in_formations[self.player_number_in_formation],
                                               destination_orientation)).exec()

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def check_success(self):
        player_position = self.player.pose.position
        distance = (player_position - self.target.position).norm()
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False
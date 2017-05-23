
# Under MIT licence, see LICENCE.txt
import math
import numpy as np
import time

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM, POSITION_DEADZONE, BALL_RADIUS, ROBOT_RADIUS
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommand, AICommandType
from ai.STA.Action.GoBehind import GoBehind

__author__ = 'RoboCupULaval'

POSITION_DEADZONE = 40
ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class Intercept(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, game_state, player_id, target=Pose(), args=None):
        Tactic.__init__(self, game_state, player_id, target, args)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.player_id = player_id
        self.player = self.game_state.game.friends.players[self.player_id]
        self.player_position = self.player.pose.position.conv_2_np()
        self.current_state = self.go_between_ball_and_target
        self.next_state = self.go_between_ball_and_target
        self.debug_interface = DebugInterface()

        self.target = target

    # def go_intercept_ball(self):
    #
    #     ball_np = self.game_state.get_ball_position().conv_2_np()
    #     vect_ball_2_robot = self.player_position - ball_np
    #     ball_velocity = self.game_state.get_ball_velocity().conv_2_np()
    #     angle_robot_ball_speed = np.arctan2(-ball_velocity[0], -ball_velocity[1]) - np.arctan2(vect_ball_2_robot[0],
    #                                                                                          vect_ball_2_robot[1])
    #     terme_1 = 2 * self.player.max_acc * np.linalg.norm(vect_ball_2_robot) ** 2
    #     terme_2 = 4 * self.player.max_acc * np.linalg.norm(vect_ball_2_robot) ** 2 * np.linalg.norm(
    #         ball_velocity) ** 2 * \
    #               np.sin(angle_robot_ball_speed) ** 2
    #     terme_3 = 4 * self.player.max_acc * np.linalg.norm(vect_ball_2_robot) * np.linalg.norm(ball_velocity) * \
    #               np.linalg.norm(self.player.velocity) * np.cos(angle_robot_ball_speed) + \
    #               np.linalg.norm(self.player.velocity) ** 2
    #     terme_4 = 2 * np.linalg.norm(vect_ball_2_robot) * np.linalg.norm(ball_velocity) * \
    #               np.cos(angle_robot_ball_speed) + np.linalg.norm(self.player.velocity)
    #     terme_5 = self.player.max_acc - 2 * np.linalg.norm(vect_ball_2_robot) ** 2
    #     print(angle_robot_ball_speed)
    #     print(terme_1)
    #     print(terme_2)
    #     print(terme_3)
    #     print(terme_4)
    #     print(terme_5)
    #     if np.abs(terme_5) < 0.1:
    #         t = np.linalg.norm(vect_ball_2_robot) ** 2 / terme_4
    #     else:
    #         t = np.abs((np.sqrt(terme_1 - terme_2 + terme_3) - terme_4) / terme_5)
    #     print(t)
    #     target = ball_np + ball_velocity * t
    #     print(target)
    #     vec_target_2_robot = self.player_position - target
    #     if np.linalg.norm(ball_velocity) < 50 and np.linalg.norm(vect_ball_2_robot) < 1000:
    #         #la balle va lentement et on va la pogner
    #         self.next_state = self.grab_ball
    #     elif np.linalg.norm(vec_target_2_robot) > 2000:
    #         #fuck off la balle est trop loin
    #         self.status_flag = Flags.FAILURE
    #         self.next_state = self.halt
    #     else:
    #         # wouf wouf
    #         self.next_state = self.go_intercept_ball
    #
    #     return GoToPositionPathfinder(self.game_state, self.player_id,
    #                                   Pose(Position.from_np(target), np.arctan2(ball_velocity[0], ball_velocity[1])))

    def go_between_ball_and_target(self):

        self.status_flag = Flags.WIP


        ball = self.game_state.get_ball_position()
        ball_velocity = self.game_state.get_ball_velocity().conv_2_np()
        if np.linalg.norm(ball_velocity) > 50:
            self.target = Pose(Position.from_np(ball.conv_2_np() - ball_velocity), 0)
            dist_behind = np.linalg.norm(ball_velocity) + 1/np.sqrt(np.linalg.norm(ball_velocity))
        else:
            self.target = None
            dist_behind = 250
        if self.target is None:
            if self.game_state.get_our_team_color() == 0: #yellow
                self.target = Pose(self.game_state.const["FIELD_GOAL_BLUE_MID_GOAL"], 0)
            else:
                self.target = Pose(self.game_state.const["FIELD_GOAL_YELLOW_MID_GOAL"], 0)
        if self._is_player_towards_ball_and_target():
                self.next_state = self.grab_ball
        else:
            # self.debug.add_log(4, "Distance from ball: {}".format(dist))
            self.next_state = self.go_between_ball_and_target

        return GoBehind(self.game_state, self.player_id, ball, self.target.position, dist_behind)

    def _is_player_towards_ball_and_target(self):

        player_x = self.game_state.game.friends.players[self.player_id].pose.position.x
        player_y = self.game_state.game.friends.players[self.player_id].pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        target_x = self.target.position.x
        target_y = self.target.position.y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_target_2_ball = np.array([ball_x - target_x, ball_y - target_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.game_state.game.friends.players[self.player_id].pose.orientation),
                                      np.sin(self.game_state.game.friends.players[self.player_id].pose.orientation)])
        # print(np.dot(vector_player_2_ball, vector_target_2_ball))
        if np.dot(vector_player_2_ball, vector_target_2_ball) < - 0.99:
            if np.dot(vector_player_dir, vector_target_2_ball) < - 0.99:
                return True
        return False

    def grab_ball(self):
        # self.debug.add_log(1, "Grab ball called")
        # self.debug.add_log(1, "vector player 2 ball : {} mm".format(self.vector_norm))
        if self._is_player_towards_ball():
            self.next_state = self.halt
        else:
            self.next_state = self.grab_ball
            self.status_flag = Flags.WIP
        # self.debug.add_log(1, "orientation go get ball {}".format(self.last_angle))
        return Grab(self.game_state, self.player_id)

    def _is_player_between_ball_and_target(self, fact=-0.99):
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        target = self.target.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        target_to_ball = ball - target
        ball_to_player /= np.linalg.norm(ball_to_player)
        target_to_ball /= np.linalg.norm(target_to_ball)
        player_dir = np.array([np.cos(self.game_state.game.friends.players[self.player_id].pose.orientation),
                               np.sin(self.game_state.game.friends.players[self.player_id].pose.orientation)])
        if np.dot(ball_to_player, target_to_ball) < fact:
            if np.dot(player_dir, ball_to_player) < fact:
                return True
        return False

    def _is_player_towards_ball(self, fact=-0.99):

        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        ball_to_player /= np.linalg.norm(ball_to_player)
        player_dir = np.array([np.cos(self.game_state.game.friends.players[self.player_id].pose.orientation),
                                      np.sin(self.game_state.game.friends.players[self.player_id].pose.orientation)])
        if np.dot(player_dir, ball_to_player) < fact:
            return True
        return False

    def _reset_ttl(self):
        super()._reset_ttl()
        if get_distance(self.last_ball_position, self.game_state.get_ball_position()) > POSITION_DEADZONE:
            self.last_ball_position = self.game_state.get_ball_position()
            self.move_action = self._generate_move_to()

    def halt(self):
        self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player_id)

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
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommand, AICommandType
from ai.STA.Action.GoBehind import GoBehind

__author__ = 'RoboCupULaval'

POSITION_DEADZONE = 40
ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class Capture(Tactic):
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

    def __init__(self, p_game_state, player_id, target=Pose(), args=None):
        Tactic.__init__(self, p_game_state, player_id, target, args)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.player_id = player_id
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.debug_interface = DebugInterface()

        self.target = target

    def get_behind_ball(self):
        # print('Etat = go_behind')
        self.status_flag = Flags.WIP

        player_x = self.game_state.game.friends.players[self.player_id].pose.position.x
        player_y = self.game_state.game.friends.players[self.player_id].pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)

        if self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
            self.orientation_target = self.game_state.game.friends.players[self.player_id].pose.orientation
        else:
            # self.debug.add_log(4, "Distance from ball: {}".format(dist))
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player_id,
                        self.game_state.get_ball_position(),
                        self.target.position,
                        120,
                        pathfinding=True)

    def grab_ball(self):
        # print('Etat = grab_ball')
        # self.debug.add_log(1, "Grab ball called")
        # self.debug.add_log(1, "vector player 2 ball : {} mm".format(self.vector_norm))
        if self._get_distance_from_ball() < 120:
            self.next_state = self.keep
        elif self._is_player_towards_ball_and_target(-0.9):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        # self.debug.add_log(1, "orientation go get ball {}".format(self.last_angle))
        return Grab(self.game_state, self.player_id)

    def keep(self):
        # print('Etat = keep')
        # self.debug.add_log(1, "Grab ball called")
        # self.debug.add_log(1, "vector player 2 ball : {} mm".format(self.vector_norm))
        if self._get_distance_from_ball() < 120:
            self.next_state = self.keep
            self.status_flag = Flags.SUCCESS
        elif self._is_player_towards_ball_and_target(-0.4):
            self.next_state = self.grab_ball
            self.status_flag = Flags.WIP
        else:
            self.next_state = self.get_behind_ball
            self.status_flag = Flags.WIP
        # self.debug.add_log(1, "orientation go get ball {}".format(self.last_angle))
        return Idle(self.game_state, self.player_id)

    def _get_distance_from_ball(self):
        return get_distance(self.game_state.get_player_pose(self.player_id).position,
                            self.game_state.get_ball_position())

    def _is_player_towards_ball_and_target(self, fact=-0.99):
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        target = self.target.position.conv_2_np()

        vector_player_2_ball = ball - player
        vector_target_2_ball = ball - target
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.game_state.game.friends.players[self.player_id].pose.orientation),
                                      np.sin(self.game_state.game.friends.players[self.player_id].pose.orientation)])
        if np.dot(vector_player_2_ball, vector_target_2_ball) < fact:
            if np.dot(vector_player_dir, vector_target_2_ball) < fact:
                return True
        return False

    def _is_player_towards_target(self, fact=-0.99):

        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        target = self.target.position.conv_2_np()

        vector_target_2_player = player - target
        vector_target_2_player /= np.linalg.norm(vector_target_2_player)
        vector_player_dir = np.array([np.cos(self.game_state.game.friends.players[self.player_id].pose.orientation),
                                      np.sin(self.game_state.game.friends.players[self.player_id].pose.orientation)])
        if np.dot(vector_player_dir, vector_target_2_player) < fact:
            return True
        return False

    def _reset_ttl(self):
        super()._reset_ttl()
        if get_distance(self.last_ball_position, self.game_state.get_ball_position()) > POSITION_DEADZONE:
            self.last_ball_position = self.game_state.get_ball_position()
            self.move_action = self._generate_move_to()

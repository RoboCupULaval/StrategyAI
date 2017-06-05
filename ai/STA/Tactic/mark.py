
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
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ai_command import AICommand, AICommandType
from ai.STA.Action.GoBehind import GoBehind

__author__ = 'RoboCupULaval'

POSITION_DEADZONE = 40
ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


class Mark(Tactic):
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
        self.enemy_id = 4
        self.current_state = self.go_between_ball_and_enemy
        self.next_state = self.go_between_ball_and_enemy
        self.debug_interface = DebugInterface()

        self.target = target

    def go_between_ball_and_enemy(self):
        self.status_flag = Flags.WIP

        enemy = self.game_state.game.friends.players[self.enemy_id].pose.position
        ball = self.game_state.get_ball_position()

        if self._is_player_between_ball_and_enemy():
            self.next_state = self.move_to_enemy
        else:
            # self.debug.add_log(4, "Distance from ball: {}".format(dist))
            self.next_state = self.go_between_ball_and_enemy
        return GoBetween(self.game_state, self.player_id, ball, enemy, ball, 300)

    def move_to_enemy(self):
        # self.debug.add_log(1, "Grab ball called")
        # self.debug.add_log(1, "vector player 2 ball : {} mm".format(self.vector_norm))
        if self._is_player_between_ball_and_enemy():
            self.next_state = self.move_to_enemy
            self.status_flag = Flags.SUCCESS
        else:
            self.next_state = self.go_between_ball_and_enemy
            self.status_flag = Flags.WIP
        # self.debug.add_log(1, "orientation go get ball {}".format(self.last_angle))
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        enemy = self.game_state.game.friends.players[self.enemy_id].pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        ball_to_enemy = enemy - ball
        player_to_ball = ball - player
        destination = enemy - 300 * ball_to_enemy / np.linalg.norm(ball_to_enemy)
        destination_orientation = np.arctan2(player_to_ball[1], player_to_ball[0])
        return MoveToPosition(self.game_state, self.player_id, Pose(Position.from_np(destination), destination_orientation))

    def _is_player_between_ball_and_enemy(self, fact=-0.99):
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        enemy = self.game_state.game.friends.players[self.enemy_id].pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        enemy_to_ball = ball - enemy
        ball_to_player /= np.linalg.norm(ball_to_player)
        enemy_to_ball /= np.linalg.norm(enemy_to_ball)
        player_dir = np.array([np.cos(self.game_state.game.friends.players[self.player_id].pose.orientation),
                               np.sin(self.game_state.game.friends.players[self.player_id].pose.orientation)])
        if np.dot(ball_to_player, enemy_to_ball) < fact:
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

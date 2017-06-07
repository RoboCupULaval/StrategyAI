# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

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
        player : Instance du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None):
        Tactic.__init__(self, game_state, player, target, args)
        # TODO enemy id ???
        self.enemy_id = 4
        self.current_state = self.go_between_ball_and_enemy
        self.next_state = self.go_between_ball_and_enemy

        self.target = target

    def go_between_ball_and_enemy(self):
        self.status_flag = Flags.WIP

        enemy = self.game_state.game.friends.players[self.enemy_id].pose.position
        ball = self.game_state.get_ball_position()

        if self._is_player_between_ball_and_enemy():
            self.next_state = self.move_to_enemy
        else:
            self.next_state = self.go_between_ball_and_enemy
        return GoBetween(self.game_state, self.player, ball, enemy, ball, 300)

    def move_to_enemy(self):
        if self._is_player_between_ball_and_enemy():
            self.next_state = self.move_to_enemy
            self.status_flag = Flags.SUCCESS
        else:
            self.next_state = self.go_between_ball_and_enemy
            self.status_flag = Flags.WIP
        player = self.player.pose.position.conv_2_np()
        enemy = self.player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        ball_to_enemy = enemy - ball
        player_to_ball = ball - player
        destination = enemy - 300 * ball_to_enemy / np.linalg.norm(ball_to_enemy)
        destination_orientation = np.arctan2(player_to_ball[1], player_to_ball[0])
        return MoveToPosition(self.game_state, self.player, Pose(Position.from_np(destination),
                                                                 destination_orientation))

    def _is_player_between_ball_and_enemy(self, fact=-0.99):
        player = self.player.pose.position.conv_2_np()
        enemy = self.game_state.get_player_position(self.enemy_id, True).conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        enemy_to_ball = ball - enemy
        ball_to_player /= np.linalg.norm(ball_to_player)
        enemy_to_ball /= np.linalg.norm(enemy_to_ball)
        player_dir = np.array([np.cos(self.player.pose.orientation),
                               np.sin(self.player.pose.orientation)])
        if np.dot(ball_to_player, enemy_to_ball) < fact:
            if np.dot(player_dir, ball_to_player) < fact:
                return True
        return False

    def _is_player_towards_ball(self, fact=-0.99):
        player = self.player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()

        ball_to_player = player - ball
        ball_to_player /= np.linalg.norm(ball_to_player)
        player_dir = np.array([np.cos(self.player.pose.orientation),
                               np.sin(self.player.pose.orientation)])
        if np.dot(player_dir, ball_to_player) < fact:
            return True
        return False

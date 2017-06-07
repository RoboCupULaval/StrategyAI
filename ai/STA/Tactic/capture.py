# Under MIT licence, see LICENCE.txt
import numpy as np

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.Idle import Idle
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

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
        player : Instance du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args=None):
        Tactic.__init__(self, game_state, player, target, args)
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.debug_interface = DebugInterface()

        self.target = target

    def get_behind_ball(self):
        self.status_flag = Flags.WIP

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)

        if self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
            # orientation_target = self.player.pose.orientation
        else:
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(),
                        self.target.position, 120, pathfinding=True)

    def grab_ball(self):
        if self._get_distance_from_ball() < 120:
            self.next_state = self.keep
        elif self._is_player_towards_ball_and_target(-0.9):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return Grab(self.game_state, self.player)

    def keep(self):
        if self._get_distance_from_ball() < 120:
            self.next_state = self.keep
            self.status_flag = Flags.SUCCESS
        elif self._is_player_towards_ball_and_target(-0.4):
            self.next_state = self.grab_ball
            self.status_flag = Flags.WIP
        else:
            self.next_state = self.get_behind_ball
            self.status_flag = Flags.WIP
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return get_distance(self.player.pose.position, self.game_state.get_ball_position())

    def _is_player_towards_ball_and_target(self, fact=-0.99):
        player = self.player.pose.position.conv_2_np()
        ball = self.game_state.get_ball_position().conv_2_np()
        target = self.target.position.conv_2_np()

        vector_player_2_ball = ball - player
        vector_target_2_ball = ball - target
        if not (np.linalg.norm(vector_player_2_ball) == 0):
            vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        if not (np.linalg.norm(vector_target_2_ball) == 0):
            vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_player_2_ball, vector_target_2_ball) < fact:
            if np.dot(vector_player_dir, vector_target_2_ball) < fact:
                return True
        return False

    def _is_player_towards_target(self, fact=-0.99):

        player = self.player.pose.position.conv_2_np()
        target = self.target.position.conv_2_np()

        vector_target_2_player = player - target
        vector_target_2_player /= np.linalg.norm(vector_target_2_player)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_player_dir, vector_target_2_player) < fact:
            return True
        return False

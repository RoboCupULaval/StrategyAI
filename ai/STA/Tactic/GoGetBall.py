# Under MIT licence, see LICENCE.txt
import time
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from ai.STA.Action.AllStar import AllStar
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.MoveToPosition import MoveToPosition


from RULEngine.Util.geometry import get_distance
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
import numpy as np
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ANGLE_DEADZONE = 0.08
COMMAND_DELAY = 0.5


class GoGetBall(Tactic):
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

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=None, args: List[str]=None):
        Tactic.__init__(self, game_state, player, target, args)
        self.current_state = self.get_behind_ball
        self.next_state = self.get_behind_ball
        self.last_ball_position = self.game_state.get_ball_position()
        self.last_angle = 0
        self.last_time = time.time()

    def get_behind_ball(self):
        self.status_flag = Flags.WIP

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)

        if self._is_player_towards_ball_and_target():
                self.last_time = time.time()
                self.next_state = self.grab_ball
        else:
            self.next_state = self.get_behind_ball
        return GoBehind(self.game_state, self.player,
                        self.game_state.get_ball_position()+Position(vector_player_2_ball[0]*70,
                                                                     vector_player_2_ball[1] * 70),
                        self.target.position,
                        self.game_state.const["DISTANCE_BEHIND"],
                        pathfinder_on=True)

    def start_dribbler(self):
        now = time.time()
        if now - self.last_time > COMMAND_DELAY:
            self.last_ball_position = self.game_state.get_ball_position()
            self.last_angle = self.player.pose.orientation
            self.next_state = self.grab_ball
        return AllStar(self.game_state, self.player, **{"dribbler_on": 2})

    def grab_ball(self):
        if self._get_distance_from_ball() < 120 and self._is_player_towards_ball_and_target():
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
        else:
            self.next_state = self.grab_ball
        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y
        angle_ball_2_target = np.arctan2(self.target.position.y - ball_y, self.target.position.x - ball_x)
        return MoveToPosition(self.game_state, self.player, Pose(Position(ball_x, ball_y), angle_ball_2_target))

    def halt(self):  # FAIRE CECI DANS TOUTE LES TACTIQUES
        if self.status_flag == Flags.INIT:
            self.next_state = self.get_behind_ball
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)


    def _get_distance_from_ball(self):
        return get_distance(self.player.pose.position, self.game_state.get_ball_position())

    def _is_player_towards_ball_and_target(self):
        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y

        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        target_x = self.target.position.x
        target_y = self.target.position.y

        vector_player_2_ball = np.array([ball_x - player_x, ball_y - player_y])
        vector_target_2_ball = np.array([ball_x - target_x, ball_y - target_y])
        vector_player_2_ball /= np.linalg.norm(vector_player_2_ball)
        vector_target_2_ball /= np.linalg.norm(vector_target_2_ball)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        # print(np.dot(vector_player_2_ball, vector_target_2_ball))
        if np.dot(vector_player_2_ball, vector_target_2_ball) < - 0.99:
            if np.dot(vector_player_dir, vector_target_2_ball) < - 0.99:
                return True
        return False

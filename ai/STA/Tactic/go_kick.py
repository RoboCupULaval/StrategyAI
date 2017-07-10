# Under MIT licence, see LICENCE.txt
from typing import List, Union
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.Algorithm.evaluation_module import best_passing_option
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Idle import Idle
from ai.STA.Action.Kick import Kick
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

COMMAND_DELAY = 0.5
TARGET_ASSIGNATION_DELAY = 1

class GoKick(Tactic):
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

    def __init__(self, game_state: GameState, player: OurPlayer,
                 target: Pose=Pose(),
                 args: List[str]=None,
                 kick_force: Union[int, float]=3,
                 auto_update_target=False):

        Tactic.__init__(self, game_state, player, target, args)
        self.current_state = self.kick_charge
        self.next_state = self.kick_charge
        self.cmd_last_time = time.time()
        self.auto_update_target = auto_update_target
        self.target_assignation_last_time = None
        self.target = target
        self._find_best_passing_option()
        self.kick_force = kick_force

    def kick_charge(self):
        if time.time() - self.cmd_last_time > COMMAND_DELAY:
            self.next_state = self.go_behind_ball
            self.cmd_last_time = time.time()

        return AllStar(self.game_state, self.player,  **{"charge_kick": True})

    def go_behind_ball(self):
        self.status_flag = Flags.WIP

        if self._is_player_towards_ball_and_target(-0.95):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            self._find_best_passing_option()
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(),
                        self.target.position, 250, pathfinder_on=True)

    def grab_ball(self):
        if self._get_distance_from_ball() < 120:
            self.next_state = self.kick
            self.cmd_last_time = time.time()
        elif self._is_player_towards_ball_and_target(-0.95):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
        return Grab(self.game_state, self.player)

    def kick(self):
        if self._get_distance_from_ball() > 100:
            self.next_state = self.halt
            self.cmd_last_time = time.time()
        elif time.time() - self.cmd_last_time < COMMAND_DELAY:
            self.next_state = self.kick
        else:
            self.next_state = self.kick_charge
        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def halt(self):  # FAIRE CECI DANS TOUTE LES TACTIQUES
        if self.status_flag == Flags.INIT:
            self.next_state = self.kick_charge
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _is_player_towards_ball_and_target(self, fact=-0.99):
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
        if np.dot(vector_player_2_ball, vector_target_2_ball) < fact:
            if np.dot(vector_player_dir, vector_target_2_ball) < fact:
                return True
        return False

    def _find_best_passing_option(self):
        if (self.auto_update_target
            and (self.target_assignation_last_time is None
                or time.time() - self.target_assignation_last_time > TARGET_ASSIGNATION_DELAY)):
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))
            self.target_assignation_last_time = time.time()

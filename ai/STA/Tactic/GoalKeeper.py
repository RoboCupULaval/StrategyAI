# Under MIT licence, see LICENCE.txt

from typing import List
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.constant import TeamColor
from ai.Algorithm.evaluation_module import closest_player_to_point, best_passing_option
from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Kick import Kick
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Action.GoBehind import GoBehind
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

TARGET_ASSIGNATION_DELAY = 1

class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession.
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du gardien de but
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        is_yellow : un booléen indiquant si le gardien est dans l'équipe des jaunes, ce qui détermine quel but est
        protégé. Les jaunes protègent le but de droite et les bleus, le but de gauche.
    """
    # TODO: À complexifier pour prendre en compte la position des joueurs adverses et la vitesse de la balle.

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None,):
        Tactic.__init__(self, game_state, player, target, args)
        self.is_yellow = self.player.team.team_color == TeamColor.YELLOW
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = Flags.WIP
        self.target_assignation_last_time = None
        self.target = target
        self._find_best_passing_option()
        self.kick_force = 5

    def kick_charge(self):
        self.next_state = self.protect_goal
        return AllStar(self.game_state, self.player,  **{"charge_kick": True})

    def protect_goal(self):
        if (self.player == closest_player_to_point(GameState().get_ball_position())
        and self._get_distance_from_ball() < 100):
            self.next_state = self.go_behind_ball
        else:
            self.next_state = self.protect_goal

        return ProtectGoal(self.game_state, self.player, self.is_yellow,
                           minimum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"]-250,
                           maximum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"])

    def go_behind_ball(self):
        if not self.player == closest_player_to_point(GameState().get_ball_position()):
            self.next_state = self.protect_goal
        elif self._is_player_towards_ball_and_target(-0.95):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            self._find_best_passing_option()
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(),
                        self.target.position, 250, pathfinder_on=True)

    def grab_ball(self):
        if not self.player == closest_player_to_point(GameState().get_ball_position()):
            self.next_state = self.protect_goal
        elif self._get_distance_from_ball() < 120:
            self.next_state = self.kick
        elif self._is_player_towards_ball_and_target(-0.95):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
        return Grab(self.game_state, self.player)

    def kick(self):
        if not self.player == closest_player_to_point(GameState().get_ball_position()):
            self.next_state = self.protect_goal
        else:
            self.next_state = self.kick_charge
        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def _get_distance_from_ball(self):
        return get_distance(self.player.pose.position,
                            self.game_state.get_ball_position())

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
        if self.target_assignation_last_time is None \
                or time.time() - self.target_assignation_last_time > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))
            self.target_assignation_last_time = time.time()

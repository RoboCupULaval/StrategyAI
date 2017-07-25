# Under MIT licence, see LICENCE.txt

from typing import List
from math import tan, pi
import time

from RULEngine.Util.constant import ROBOT_RADIUS
from RULEngine.Game.Field import FieldSide
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import clamp, compare_angle, wrap_to_pi
from RULEngine.Util.constant import TeamColor
from ai.Algorithm.evaluation_module import closest_player_to_point, best_passing_option, player_with_ball

from ai.STA.Action.AllStar import AllStar
from ai.STA.Action.Kick import Kick
from ai.STA.Action.grab import Grab
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.MoveToPosition import MoveToPosition
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

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(),
                 penalty_kick=False, args: List[str]=None,):
        Tactic.__init__(self, game_state, player, target, args)
        self.is_yellow = self.player.team.team_color == TeamColor.YELLOW
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = Flags.WIP
        self.target_assignation_last_time = None
        self.target = target
        self._find_best_passing_option()
        self.kick_force = 5
        self.penalty_kick = penalty_kick

    def kick_charge(self):
        self.next_state = self.protect_goal
        return AllStar(self.game_state, self.player,  **{"charge_kick": True})

    def protect_goal(self):
        if not self.penalty_kick:
            if self.player == closest_player_to_point(GameState().get_ball_position()).player and\
                            self._get_distance_from_ball() < 100:
                self.next_state = self.go_behind_ball
            else:
                self.next_state = self.protect_goal
            return ProtectGoal(self.game_state, self.player, self.is_yellow,
                               minimum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"]-250,
                               maximum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"])
        else:
            our_goal = Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"], 0)
            opponent_kicker = player_with_ball(2*ROBOT_RADIUS)
            ball_position = self.game_state.get_ball_position()
            if opponent_kicker is not None:
                ball_to_goal = our_goal.x - ball_position.x

                if self.game_state.field.our_side is FieldSide.POSITIVE:
                    opponent_kicker_orientation = clamp(opponent_kicker.pose.orientation, -pi/5, pi/5)
                    goalkeeper_orientation = wrap_to_pi(opponent_kicker_orientation - pi)
                else:
                    opponent_kicker_orientation = clamp(wrap_to_pi(opponent_kicker.pose.orientation - pi), -pi/5, pi/5)
                    goalkeeper_orientation = opponent_kicker_orientation

                y_position_on_line = ball_to_goal * tan(opponent_kicker_orientation)
                y_position_on_line = clamp(y_position_on_line,
                                           -GameState().const["FIELD_GOAL_WIDTH"]/4,
                                           GameState().const["FIELD_GOAL_WIDTH"]/4)

                return MoveToPosition(self.game_state,
                              self.player,
                              Pose(our_goal.x, y_position_on_line, goalkeeper_orientation),
                              pathfinder_on=True,
                              cruise_speed=2)
            else:
                return MoveToPosition(self.game_state,
                              self.player,
                              Pose(our_goal),
                              pathfinder_on=True,
                              cruise_speed=2)

    def go_behind_ball(self):
        if not self.player == closest_player_to_point(GameState().get_ball_position()).player:
            self.next_state = self.protect_goal
        elif self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
            self._find_best_passing_option()
        return GoBehind(self.game_state, self.player, self.game_state.get_ball_position(),
                        self.target.position, 250, pathfinder_on=True)

    def grab_ball(self):
        if not self.player == closest_player_to_point(GameState().get_ball_position()).player:
            self.next_state = self.protect_goal
        elif self._get_distance_from_ball() < 120:
            self.next_state = self.kick
        elif self._is_player_towards_ball_and_target():
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball
        return Grab(self.game_state, self.player)

    def kick(self):
        if not self.player == closest_player_to_point(GameState().get_ball_position()).player:
            self.next_state = self.protect_goal
        else:
            self.next_state = self.kick_charge
        return Kick(self.game_state, self.player, self.kick_force, self.target)

    def _get_distance_from_ball(self):
        return (self.player.pose.position - self.game_state.get_ball_position()).norm()

    def _is_player_towards_ball_and_target(self, abs_tol=pi/30):
        ball_position = self.game_state.get_ball_position()
        target_to_ball = ball_position - self.target.position
        ball_to_player = self.player.pose.position - ball_position
        return compare_angle(target_to_ball.angle(), ball_to_player.angle(), abs_tol=abs_tol)

    def _find_best_passing_option(self):
        if self.target_assignation_last_time is None \
                or time.time() - self.target_assignation_last_time > TARGET_ASSIGNATION_DELAY:
            tentative_target_id = best_passing_option(self.player)
            if tentative_target_id is None:
                self.target = Pose(Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"], 0), 0)
            else:
                self.target = Pose(GameState().get_player_position(tentative_target_id))
            self.target_assignation_last_time = time.time()

# Under MIT licence, see LICENCE.txt

from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import DISTANCE_BEHIND, TeamColor
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.GoBehind import GoBehind
from ai.Util.ball_possession import can_get_ball, has_ball
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'


class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession. Il s'agit d'une version simple, mais fonctionelle du gardien. Peut être améliorer.
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
    # TODO: À complexifier pour prendre en compte la position des jouers adverses et la vitesse de la balle.

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None,):
        Tactic.__init__(self, game_state, player, target, args)
        self.is_yellow = self.player.team.team_color == TeamColor.YELLOW_TEAM
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = Flags.WIP

    def protect_goal(self):
        ball_position = self.game_state.get_ball_position()
        if not self.game_state.game.field.is_inside_goal_area(ball_position, self.is_yellow):
            self.next_state = self.protect_goal
        else:
            self.next_state = self.go_behind_ball
        self.target = Pose(self.game_state.get_ball_position())
        return ProtectGoal(self.game_state, self.player, self.is_yellow,
                           minimum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"])

    def go_behind_ball(self):
        ball_position = self.game_state.get_ball_position()
        if not self.game_state.game.field.is_inside_goal_area(ball_position, self.is_yellow):
            self.next_state = self.protect_goal
        else:
            if can_get_ball(self.game_state, self.player_id, ball_position):
                self.next_state = self.grab_ball
            else:
                self.next_state = self.go_behind_ball

        return GoBehind(self.game_state, self.player, ball_position, Position(0, 0), DISTANCE_BEHIND)

    def grab_ball(self):
        ball_position = self.game_state.get_ball_position()

        if has_ball(self.game_state, self.player_id):
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
        elif can_get_ball(self.game_state, self.player_id, ball_position):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball  # back to go_behind; the ball has moved
        return GetBall(self.game_state, self.player)

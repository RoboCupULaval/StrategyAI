# Under MIT licence, see LICENCE.txt
from RULEngine.Util.geometry import is_path_clear
from .Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags, DEFAULT_TIME_TO_LIVE
from ..Action.ProtectGoal import ProtectGoal
from ai.STA.Action.GetBall import GetBall
from ai.STA.Action.GoBehind import GoBehind
from ai.Util.ball_possession import can_get_ball, has_ball
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM, DISTANCE_BEHIND, TeamColor

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

    def __init__(self, p_game_state, p_player_id, target=Pose(), args=None,
                 time_to_live=DEFAULT_TIME_TO_LIVE):
        Tactic.__init__(self, p_game_state, p_player_id, target, args)
        assert isinstance(p_player_id, int)
        assert PLAYER_PER_TEAM >= p_player_id >= 0

        self.player_id = p_player_id
        self.is_yellow = self.game_state.get_our_team_color == TeamColor.YELLOW_TEAM
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = Flags.WIP
        # print(self.game_state.game.field.constant["FIELD_GOAL_RADIUS"])

    def protect_goal(self):

        ball_position = self.game_state.get_ball_position()
        # print(self.game_state.game.field.is_inside_goal_area(ball_position, self.is_yellow))
        if not self.game_state.game.field.is_inside_goal_area(ball_position, self.is_yellow):
            self.next_state = self.protect_goal
        else:
            self.next_state = self.go_behind_ball
        self.target = Pose(self.game_state.get_ball_position())
        return ProtectGoal(self.game_state, self.player_id, self.is_yellow,
                           p_minimum_distance=self.game_state.game.field.constant["FIELD_GOAL_RADIUS"])

    def go_behind_ball(self):
        ball_position = self.game_state.get_ball_position()
        if not self.game_state.game.field.is_inside_goal_area(ball_position, self.is_yellow):
            self.next_state = self.protect_goal
        else:
            if can_get_ball(self.game_state, self.player_id, ball_position):
                self.next_state = self.grab_ball
            else:
                self.next_state = self.go_behind_ball

        return GoBehind(self.game_state, self.player_id, ball_position, Position(0, 0), DISTANCE_BEHIND)

    def grab_ball(self):
        ball_position = self.game_state.get_ball_position()

        if has_ball(self.game_state, self.player_id):
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
        elif can_get_ball(self.game_state, self.player_id, ball_position):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball  # back to go_behind; the ball has moved
        return GetBall(self.game_state, self.player_id)

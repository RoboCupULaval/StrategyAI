# Under MIT licence, see LICENCE.txt

from .Tactic import Tactic
from ai.STA.Tactic import tactic_constants
from ..Action.ProtectGoal import ProtectGoal
from ai.STA.Action.GrabBall import GrabBall
from ai.STA.Action.GoBehind import GoBehind
from ai.STA.Action.Idle import Idle
from RULEngine.Util.Position import Position
from RULEngine.Util.area import isInsideGoalArea, player_can_grab_ball, player_grabbed_ball
from RULEngine.Util.constant import PLAYER_PER_TEAM, DISTANCE_BEHIND

__author__ = 'RoboCupULaval'


class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession. Il s'agit d'une version simple, mais fonctionelle du gardien. Peut être améliorer.
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du gardien de but
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        is_yellow : un booléen indiquant si le gardien est dans l'équipe des jaunes, ce qui détermine quel but est
        protégé. Les jaunes protègent le but de droite et les bleus, le but de gauche.
    """
    # TODO: À complexifier pour prendre en compte la position des jouers adverses et la vitesse de la balle.

    def __init__(self, p_info_manager, p_player_id, p_is_yellow=False):
        Tactic.__init__(self, p_info_manager)
        assert isinstance(p_player_id, int)
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert isinstance(p_is_yellow, bool)

        self.player_id = p_player_id
        self.is_yellow = p_is_yellow
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal
        self.status_flag = tactic_constants.WIP

    def protect_goal(self):
        # FIXME : enlever ce hack de merde
        target_dict = {'skill': None, 'goal': None, 'target': self.info_manager.get_ball_position()}
        self.info_manager.set_player_skill_target_goal(self.player_id, target_dict)
        if not isInsideGoalArea(self.info_manager.get_ball_position(), self.is_yellow):
            self.next_state = self.protect_goal
        else:
            if player_can_grab_ball(self.info_manager, self.player_id):
                self.next_state = self.grab_ball
            else:
                self.next_state = self.go_behind_ball

        return ProtectGoal(self.info_manager, self.player_id, self.is_yellow, p_minimum_distance=300)

    def go_behind_ball(self):
        ball_position = self.info_manager.get_ball_position()

        if player_can_grab_ball(self.info_manager, self.player_id):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball

        return GoBehind(self.info_manager, self.player_id, ball_position, Position(0, 0), DISTANCE_BEHIND)

    def grab_ball(self):
        if player_grabbed_ball(self.info_manager, self.player_id):
            self.next_state = self.halt
            self.status_flag = tactic_constants.SUCCESS
        elif player_can_grab_ball(self.info_manager, self.player_id):
            self.next_state = self.grab_ball
        else:
            self.next_state = self.go_behind_ball  # back to go_behind; the ball has moved
        return GrabBall(self.info_manager, self.player_id)

# Under MIT licence, see LICENCE.txt

from .Tactic import Tactic
from ..Action.ProtectGoal import ProtectGoal
from RULEngine.Util.area import isInsideGoalArea
from RULEngine.Util.constant import PLAYER_PER_TEAM

__author__ = 'RoboCupULaval'


class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession. Il s'agit d'une version simple, mais fonctionelle du gardien. Peut être améliorer.
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

    def protect_goal(self):
        if not isInsideGoalArea(self.info_manager.get_ball_position(), self.is_yellow):
            self.next_state = self.protect_goal
        else:
            pass

        return ProtectGoal(self.info_manager, self.player_id, self.is_yellow)

    def go_behind_ball(self):
        pass

    def grab_ball(self):
        pass

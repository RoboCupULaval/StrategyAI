from .Tactic import Tactic
from ..Action.ProtectGoal import ProtectGoal

__author__ = 'RoboCupULaval'


class GoalKeeper(Tactic):
    """
    Tactique du gardien de but standard. Le gardien doit se placer entre la balle et le but, tout en restant à
    l'intérieur de son demi-cercle. Si la balle entre dans son demi-cercle, le gardien tente d'aller en prendre
    possession. Il s'agit d'une version simple, mais fonctionelle du gardien. Peut être améliorer.
    """
    # TODO: À complexifier pour prendre en compte la position des jouers adverses et la vitesse de la balle.

    def __init__(self, p_info_manager, p_player_id):
        Tactic.__init__(self, p_info_manager)
        assert isinstance(p_player_id, int)

        self.player_id = p_player_id
        self.current_state = self.protect_goal
        self.next_state = self.protect_goal

    def protect_goal(self):
        pass

    def go_behind_ball(self):
        pass

    def grab_ball(self):
        pass

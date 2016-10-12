# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.CoverZone import CoverZone
from . Strategy import Strategy

class SimpleDefense(Strategy):
    def __init__(self, p_gamestatemanager, p_playmanager):
        tactics =   [GoalKeeper(p_gamestatemanager, p_playmanager, 0),
                     GoGetBall(p_gamestatemanager, p_playmanager, 1),
                     CoverZone(p_gamestatemanager, p_playmanager, 2, FIELD_Y_TOP, 0, FIELD_X_LEFT, FIELD_X_LEFT / 2),
                     CoverZone(p_gamestatemanager, p_playmanager, 3, 0, FIELD_Y_BOTTOM, FIELD_X_LEFT, FIELD_X_LEFT / 2),
                     CoverZone(p_gamestatemanager, p_playmanager, 4, FIELD_Y_TOP, 0, FIELD_X_LEFT / 2, 0),
                     CoverZone(p_gamestatemanager, p_playmanager, 5, 0, FIELD_Y_BOTTOM, FIELD_X_LEFT / 2, 0)]
        super().__init__(p_gamestatemanager, p_playmanager, tactics)

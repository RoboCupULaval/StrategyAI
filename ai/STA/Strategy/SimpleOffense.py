# Under MIT license, see LICENSE.txt

from RULEngine.Util.constant import *
from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Action.ProtectGoal import ProtectGoal
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from ai.STA.Tactic.GoToPosition import GoToPosition
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.CoverZone import CoverZone
from . Strategy import Strategy

# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire

class SimpleOffense(Strategy):
    def __init__(self, p_info_manager):
        tactics =   [GoalKeeper(p_info_manager, 0),
                     GoGetBall(p_info_manager, 1),
                     GoGetBall(p_info_manager, 2),
                     GoGetBall(p_info_manager, 3),
                     GoGetBall(p_info_manager, 4),
                     GoGetBall(p_info_manager, 5)]
        super().__init__(p_info_manager, tactics)

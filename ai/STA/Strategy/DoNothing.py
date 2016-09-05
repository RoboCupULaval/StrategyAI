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

class DoNothing(Strategy):
    def __init__(self, p_info_manager):
        tactics =   [Stop(p_info_manager, 4)]
        super().__init__(p_info_manager, tactics)
 

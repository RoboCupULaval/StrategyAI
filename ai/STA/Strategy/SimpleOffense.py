# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.GoalKeeper import GoalKeeper
from . Strategy import Strategy

# stratégie: tout le monde fonce vers la balle car c'est tout ce qu'on sait faire

class SimpleOffense(Strategy):
    def __init__(self, p_gamestatemanager, p_playmanager):
        tactics =   [GoalKeeper(p_gamestatemanager, p_playmanager, 0),
                     GoGetBall(p_gamestatemanager, p_playmanager, 1),
                     GoGetBall(p_gamestatemanager, p_playmanager, 2),
                     GoGetBall(p_gamestatemanager, p_playmanager, 3),
                     GoGetBall(p_gamestatemanager, p_playmanager, 4),
                     GoGetBall(p_gamestatemanager, p_playmanager, 5)]
        super().__init__(p_gamestatemanager, p_playmanager, tactics)

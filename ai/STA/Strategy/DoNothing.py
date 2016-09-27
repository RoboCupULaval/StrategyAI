from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop


class DoNothing(Strategy):
    def __init__(self, p_gamestatemanager):
        tactics = [Stop(p_gamestatemanager, 0),
                   Stop(p_gamestatemanager, 1),
                   Stop(p_gamestatemanager, 2),
                   Stop(p_gamestatemanager, 3),
                   Stop(p_gamestatemanager, 4),
                   Stop(p_gamestatemanager, 5)]

        super().__init__(p_gamestatemanager, tactics)

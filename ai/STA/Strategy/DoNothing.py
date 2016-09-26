from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop


class DoNothing(Strategy):
    def __init__(self, p_gamestatemanager, p_playmanager):
        tactics = [Stop(p_gamestatemanager, p_playmanager, 0),
                   Stop(p_gamestatemanager, p_playmanager, 1),
                   Stop(p_gamestatemanager, p_playmanager, 2),
                   Stop(p_gamestatemanager, p_playmanager, 3),
                   Stop(p_gamestatemanager, p_playmanager, 4),
                   Stop(p_gamestatemanager, p_playmanager, 5)]

        super().__init__(p_gamestatemanager, p_playmanager, tactics)

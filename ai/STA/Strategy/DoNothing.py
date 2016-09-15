from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop


class DoNothing(Strategy):
    def __init__(self, p_info_manager):
        tactics = [Stop(p_info_manager, 0),
                   Stop(p_info_manager, 1),
                   Stop(p_info_manager, 2),
                   Stop(p_info_manager, 3),
                   Stop(p_info_manager, 4),
                   Stop(p_info_manager, 5)]

        super().__init__(p_info_manager, tactics)

from . Strategy import Strategy
from ai.STA.Tactic.Stop import Stop
from ai.STA.Tactic.GoToPositionNoPathfinder import GoToPositionNoPathfinder


class TestStrategy(Strategy):
    def __init__(self, p_game_state):
        tactics = [GoToPositionNoPathfinder(p_game_state, 0),
                   Stop(p_game_state, 1),
                   Stop(p_game_state, 2),
                   Stop(p_game_state, 3),
                   Stop(p_game_state, 4),
                   Stop(p_game_state, 5)]

        super().__init__(p_game_state, tactics)

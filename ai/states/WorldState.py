from ai.Debug.DebugState import DebugState
from ai.states.GameState import GameState
from ai.states.PlayState import PlayState


class WorldState:
    def __init__(self, mode_debug_active=True):
        self.mode_debug_active = mode_debug_active

        self.play_state = PlayState()
        self.game_state = GameState()

        if mode_debug_active:
            self.debug_state = DebugState()

    def update(self, game_state):
        self.game_state.update(game_state)

        if self.mode_debug_active:
            self.debug_state.update(game_state.debug)

# Under MIT License, see LICENSE.txt

from ai.Debug.debug_interface import DebugInterface
from ai.states.debug_state import DebugState
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from ai.states.module_state import ModuleState


class WorldState:
    def __init__(self, is_team_yellow=False, mode_debug_active=True):
        self.mode_debug_active = mode_debug_active
        self.module_state = ModuleState()
        self.play_state = PlayState()
        self.game_state = GameState()

        if mode_debug_active:
            self.debug_state = DebugState()
            self.debug_interface = DebugInterface()

    def update(self, game_state):
        self.game_state.update(game_state)

        if self.mode_debug_active:
            self.debug_state.update(game_state.debug)

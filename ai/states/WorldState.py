# Under MIT License, see LICENSE.txt

from ai.Debug.DebugInterface import DebugInterface
from ai.states.DebugState import DebugState
from ai.states.GameState import GameState
from ai.states.PlayState import PlayState
from ai.states.ModuleState import ModuleState


class WorldState:
    def __init__(self, is_team_yellow=False, mode_debug_active=True):
        self.mode_debug_active = mode_debug_active
        self.module_state = ModuleState()
        self.play_state = PlayState()
        self.game_state = GameState()

        if mode_debug_active:
            self.debug_state = DebugState()
            self.debug_interface = DebugInterface(self.debug_state)

    def update(self, game_state):
        self.game_state.update(game_state)

        if self.mode_debug_active:
            self.debug_state.update(game_state.debug)

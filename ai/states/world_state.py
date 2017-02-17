
# Under MIT License, see LICENSE.txt

from RULEngine.Debug.debug_interface import DebugInterface
from ai.states.game_state import GameState
from ai.states.module_state import ModuleState
from ai.states.play_state import PlayState


class WorldState:
    def __init__(self, mode_debug_active=True):
        self.module_state = ModuleState()
        self.play_state = PlayState()
        self.game_state = GameState()

        self.debug_interface = DebugInterface()

    def update(self):
        pass

    def set_reference(self, world_reference):
        self.game_state.set_reference(world_reference)

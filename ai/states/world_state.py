
# Under MIT License, see LICENSE.txt

from RULEngine.Debug.debug_interface import DebugInterface
from ai.states.game_state import GameState
from ai.states.module_state import ModuleState
from ai.states.play_state import PlayState


class WorldState:
    def __init__(self, mode_debug_active: bool=True):
        """
        initialisation du worldstate

        :param mode_debug_active: (bool) indique si le mode debug est activé
        """
        self.module_state = ModuleState()
        self.play_state = PlayState()
        self.game_state = GameState()

        # pour passer une interface de debug deja recuperer
        self.debug_interface = DebugInterface()

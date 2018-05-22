# Under MIT license, see LICENSE.txt

from Util.role import Role
from Util.role_mapping_rule import keep_prev_mapping_otherwise_random
from ai.STA.Strategy.defense_wall import DefenseWall
from ai.states.game_state import GameState


# noinspection
class DefenseWallNoKick(DefenseWall):
    def __init__(self, game_state: GameState, number_of_players: int = 4):
        super().__init__(game_state, can_kick=False)


# Under MIT license, see LICENSE.txt
from Util import Pose
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class Stop(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args=None):
        super().__init__(game_state, player, target, args, forbidden_areas=[])
        self.status_flag = Flags.SUCCESS

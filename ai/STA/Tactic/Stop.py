# Under MIT license, see LICENSE.txt
from RULEngine.Game.Player import Player
from RULEngine.Util.Pose import Pose
from ai.states.game_state import GameState
from .Tactic import Tactic
from . tactic_constants import Flags


class Stop(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args=None):
        super().__init__(game_state, player, target, args)
        self.status_flag = Flags.SUCCESS

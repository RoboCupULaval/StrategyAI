# Under MIT license, see LICENSE.txt
from RULEngine.GameDomainObjects.player import Player
from Util.Pose import Pose
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class Stop(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args=None):
        super().__init__(game_state, player, target, args)
        self.status_flag = Flags.SUCCESS

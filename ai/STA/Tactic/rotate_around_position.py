# Under MIT license, see LICENSE.txt
from typing import List

from RULEngine.GameDomainObjects.player import Player
from Util import Pose
from ai.STA.Action.rotate_around import RotateAround
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class RotateAroundPosition(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.radius = 90 if not args else float(args[0])

    def exec(self):
        orientation = (self.target.position - self.player.pose.position).angle()
        return RotateAround(self.game_state, self.player, Pose(self.target.position, orientation), self.radius).exec()

# Under MIT license, see LICENSE.txt
from typing import List
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Util.area import stayOutsideCircle
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class StayAwayFromBall(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose, keepout_radius: int = 500, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        if len(args) >= 1:
            self.keepout_radius = args[0]
        else:
            self.keepout_radius = keepout_radius

    def exec(self):
        position = stayOutsideCircle(self.player.pose.position,
                                     self.game_state.get_ball_position(),
                                     self.keepout_radius)
        return GoToPositionPathfinder(self.game_state, self.player,
                                      Pose(position, self.player.pose.orientation)).exec()

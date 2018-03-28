# Under MIT license, see LICENSE.txt
from typing import List

import numpy as np

from Util import Pose
from Util.ai_command import CmdBuilder
from Util.area import stayOutsideCircle
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class StayAwayFromBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose = Pose(),
                 args: List[str]=None, keepout_radius: int = 500):
        super().__init__(game_state, player, target, args)
        self.current_state = self.stay_out_of_circle
        self.next_state = self.stay_out_of_circle
        self.keepout_radius = keepout_radius

    def stay_out_of_circle(self):
        position = stayOutsideCircle(self.player.pose.position,
                                     self.game_state.get_ball_position(),
                                     self.keepout_radius)
        return CmdBuilder().addMoveTo(Pose(position, self.player.pose.orientation)).build()

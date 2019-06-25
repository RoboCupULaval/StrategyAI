# Under MIT license, see LICENSE.txt

from typing import List

import numpy as np

from Util import Pose
from Util.ai_command import CmdBuilder
from Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT, ROBOT_DIAMETER
from Util.geometry import compare_angle
from ai.GameDomainObjects.player import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class TestPivot(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose,
                 args: List[str]=None, target_radius=1000):
        super().__init__(game_state, player, target, args)

        self.current_state = self.move
        self.next_state = self.move
        self.target = target
        self.status_flag = Flags.INIT
        self.target_radius = float(args[0]) if len(self.args) > 0 else target_radius
        self.target_angle = (target.position - player.position).angle + np.deg2rad(90)

    def move(self):
        return CmdBuilder().addPivotTo(self.target, target_angle=self.target_angle, target_radius=self.target_radius, cruise_speed=0.4).build()



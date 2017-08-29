# Under MIT license, see LICENSE.txt

from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.states.game_state import GameState
from .Tactic import Tactic
from . tactic_constants import Flags
from ai.STA.Action.MoveToPosition import MoveToPosition

from RULEngine.Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT


class GoToPositionNoPathfinder(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        if self.args:
            self.cruise_speed = float(args[0])
        else:
            self.cruise_speed = 1

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        return MoveToPosition(self.game_state,
                              self.player,
                              self.target,
                              pathfinder_on=False,
                              cruise_speed=self.cruise_speed).exec()

    def check_success(self):
        distance = (self.player.pose - self.target).position.norm()
        if distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.target, abs_tol=ANGLE_TO_HALT):
            return True
        return False

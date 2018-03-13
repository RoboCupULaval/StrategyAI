# Under MIT license, see LICENSE.txt

from typing import List

from Util import Pose
from Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT
from ai.GameDomainObjects import Player
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyArgumentList
class GoToPositionNoPathfinder(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        self.cruise_speed = float(args[0]) if self.args else 1

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
        distance = (self.player.pose - self.target).position.norm
        return distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.target, abs_tol=ANGLE_TO_HALT)

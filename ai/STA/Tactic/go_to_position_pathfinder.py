# Under MIT license, see LICENSE.txt
from typing import List

from Util import Pose
from Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT
from ai.GameDomainObjects.player import Player
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class GoToPositionPathfinder(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose,
                 args: List[str]=None, collision_ball=False, cruise_speed=1, charge_kick=False, end_speed=0):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        self.collision_ball = collision_ball
        self.charge_kick = charge_kick
        self.end_speed = end_speed
        self.cruise_speed = float(args[0]) if len(self.args) > 0 else cruise_speed

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        return MoveToPosition(self.game_state,
                              self.player,
                              self.target).exec()

    def check_success(self):
        distance = (self.player.pose - self.target).position.norm()
        return distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.target, abs_tol=ANGLE_TO_HALT)

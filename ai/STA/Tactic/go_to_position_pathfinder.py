# Under MIT license, see LICENSE.txt
from math import pi
from typing import List

from Util import Pose
from Util.ai_command import CmdBuilder
from Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT
from Util.geometry import compare_angle
from ai.GameDomainObjects.player import Player
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class GoToPositionPathfinder(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose,
                 args: List[str]=None, ball_collision=True, cruise_speed=1, charge_kick=False, end_speed=0):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        self.ball_collision = ball_collision
        self.charge_kick = charge_kick
        self.end_speed = end_speed
        self.cruise_speed = float(args[0]) if len(self.args) > 0 else cruise_speed
        print("Assign move to position to robot id {}".format(self.player.id))

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        return CmdBuilder().addMoveTo(self.target,
                                      cruise_speed=self.cruise_speed,
                                      end_speed=self.end_speed,
                                      ball_collision=self.ball_collision).build()

    def check_success(self):
        distance = (self.player.pose - self.target).position.norm
        return distance < POSITION_DEADZONE and compare_angle(self.player.pose.orientation, self.target.orientation, abs_tol=ANGLE_TO_HALT)

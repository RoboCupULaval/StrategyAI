# Under MIT license, see LICENSE.txt
from typing import List

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose

from ai.states.game_state import GameState
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.MoveToPosition import MoveToPosition
from RULEngine.Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT


class GoToPositionPathfinder(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose,
                 args: List[str]=None, collision_ball=False, cruise_speed=2, charge_kick=False, end_speed=0):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        self.collision_ball = collision_ball
        self.charge_kick = charge_kick
        self.end_speed = end_speed
        if len(self.args) > 0:
            self.cruise_speed = float(args[0])
        else:
            self.cruise_speed = cruise_speed

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        if self.charge_kick:
            return MoveToPosition(self.game_state,
                                  self.player,
                                  self.target, pathfinder_on=True,
                                  cruise_speed=self.cruise_speed,
                                  collision_ball=self.collision_ball,
                                  charge_kick=self.charge_kick,
                                  end_speed=self.end_speed).exec()
        else:
            return MoveToPosition(self.game_state,
                                  self.player,
                                  self.target, pathfinder_on=True,
                                  cruise_speed=self.cruise_speed,
                                  collision_ball=self.collision_ball,
                                  end_speed=self.end_speed).exec()

    def check_success(self):
        distance = (self.player.pose - self.target).position.norm()
        if distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.target, abs_tol=ANGLE_TO_HALT):
            return True
        return False

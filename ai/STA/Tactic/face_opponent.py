# Under MIT license, see LICENSE.txt
import math
from typing import List

import numpy as np

from Util import Pose
from Util.ai_command import CmdBuilder
from Util.constant import POSITION_DEADZONE, ANGLE_TO_HALT
from ai.Algorithm.evaluation_module import closest_player_to_point
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


# noinspection PyArgumentList,PyArgumentList,PyArgumentList,PyArgumentList,PyArgumentList,PyAttributeOutsideInit,PyTypeChecker
class FaceOpponent(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose,
                 args: List[str]=None, distance=500, ball_collision=False,
                 cruise_speed=2, charge_kick=False, end_speed=0, dribbler_on=False):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.distance = distance
        self.status_flag = Flags.INIT
        self.ball_collision = ball_collision
        self.charge_kick = charge_kick
        self.end_speed = end_speed
        self.dribbler_on = dribbler_on
        self.cruise_speed = cruise_speed

        self.next_state = self.main_state

    def main_state(self):
        target_player = closest_player_to_point(self.game_state.ball_position, our_team=False).player
        orientation_opponent = np.array([math.cos(target_player.pose.orientation),
                                         math.sin(target_player.pose.orientation)])
        destination_position = target_player.pose.position + self.distance * orientation_opponent
        ball_to_player = self.game_state.ball_position - self.player.pose.orientation
        destination_orientation = ball_to_player.angle

        if self.check_success():
            self.status_flag = Flags.SUCCESS
        else:
            self.status_flag = Flags.WIP

        return CmdBuilder().addMoveTo(Pose(destination_position, destination_orientation),
                                      cruise_speed=self.cruise_speed,
                                      ball_collision=self.ball_collision,
                                      end_speed=self.end_speed).addChargeKicker().addForceDribbler().build()

    def check_success(self):
        distance = (self.player.pose - self.target).position.norm
        return distance < POSITION_DEADZONE and self.player.pose.compare_orientation(self.target, abs_tol=ANGLE_TO_HALT)


# Under MIT license, see LICENSE.txt
import time
from typing import List, Optional

from Util import Pose, Position
from ai.GameDomainObjects import Player
from ai.STA.Action.Idle import Idle
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

MOVING_THRESHOLD = 10  # mm


class MeasureLoopDelay(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: Optional[List[str]]=None):
        super().__init__(game_state, player, target, args)
        self.target = target
        self.status_flag = Flags.INIT
        self.next_state = self.move

        self.init_position = Position()
        self.send_command_time = 0
        self.start_moving_time = 0
        self.loop_delay = 0

    def move(self):
        self.status_flag = Flags.WIP
        self.send_command_time = time.time()
        self.next_state = self.is_moving
        self.init_position = self.player.pose.position
        return MoveToPosition(self.game_state, self.player, self.target)

    def is_moving(self):
        if (self.player.pose.position - self.init_position).norm() > MOVING_THRESHOLD:
            self.start_moving_time = time.time()
            self.loop_delay = self.start_moving_time - self.send_command_time
            print('Delay of the AI loop is {:5.3f} second'.format(self.loop_delay))
            self.next_state = self.halt
        else:
            self.next_state = self.is_moving

        return MoveToPosition(self.game_state, self.player, self.target)

    def halt(self):
        if self.status_flag == Flags.INIT:
            self.next_state = self.move
        else:
            self.status_flag = Flags.SUCCESS
        return Idle(self.game_state, self.player)


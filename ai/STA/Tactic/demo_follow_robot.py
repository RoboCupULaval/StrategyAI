# Under MIT licence, see LICENCE.txt
from typing import List

from Util import Pose
from Util.constant import POSITION_DEADZONE, ROBOT_RADIUS

from ai.GameDomainObjects import Player
from ai.STA.Action.Idle import Idle
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState

FOLLOW_SPEED = 1.5


class DemoFollowRobot(Tactic):
    def __init__(self, game_state: GameState, player: Player, p_target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, p_target, args)
        self.robot_to_follow_id = int(args[0])
        self.current_state = self.halt
        self.next_state = self.halt

    def move_to_ball(self):
        self.status_flag = Flags.WIP
        self.target = self.game_state.get_player_pose(self.robot_to_follow_id)

        if (self.player.pose.position - self.target.position).norm < POSITION_DEADZONE + ROBOT_RADIUS:
            self.next_state = self.halt
        else:
            self.next_state = self.move_to_ball

        return MoveToPosition(self.game_state, self.player, self.target)

    def halt(self):
        self.status_flag = Flags.SUCCESS

        if (self.player.pose.position - self.game_state.get_ball_position()) < POSITION_DEADZONE + ROBOT_RADIUS:
            self.next_state = self.halt
        else:
            self.next_state = self.move_to_ball
        return Idle(self.game_state, self.player)

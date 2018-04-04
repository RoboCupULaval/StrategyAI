# Under MIT licence, see LICENCE.txt
from typing import List

from Util import Pose
from Util.constant import POSITION_DEADZONE, ROBOT_RADIUS

from ai.GameDomainObjects import Player
from Util.ai_command import Idle, CmdBuilder, MoveTo
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


FOLLOW_SPEED = 1.5


class DemoFollowBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, p_target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, p_target, args)
        self.current_state = self.move_to_ball
        self.next_state = self.move_to_ball

    def move_to_ball(self):
        ball_position = self.game_state.ball_position

        if (self.player.pose.position - ball_position).norm < POSITION_DEADZONE + ROBOT_RADIUS:
            self.status_flag = Flags.SUCCESS
            return Idle
        else:
            self.status_flag = Flags.WIP
            return MoveTo(ball_position)

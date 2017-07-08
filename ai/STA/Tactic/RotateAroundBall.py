# Under MIT license, see LICENSE.txt
from typing import List
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.rotate_around import RotateAround
from ai.states.game_state import GameState


class RotateAroundBall(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.radius = 200 if not args else float(args[0])
        self.target = target

    def exec(self):
        ball_position = self.game_state.get_ball_position()
        orientation = (ball_position - self.player.pose.position).angle()
        return RotateAround(self.game_state,
                            self.player,
                            Pose(ball_position, orientation),
                            self.radius,
                            heading=self.target).exec()

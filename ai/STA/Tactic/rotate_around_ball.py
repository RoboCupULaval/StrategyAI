# Under MIT license, see LICENSE.txt
from typing import List

from RULEngine.Util.Pose import Pose

from RULEngine.GameDomainObjects.player import Player
from ai.STA.Action.rotate_around import RotateAround
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class RotateAroundBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.radius = 200 if not args else float(args[0])
        self.target = target

    def exec(self):
        ball_position = self.game_state.get_ball_position()
        orientation = (ball_position - self.player.pose.position).angle()
        target = Pose(ball_position, orientation)
        return RotateAround(self.game_state, self.player, target, self.radius, aiming=self.target).exec()

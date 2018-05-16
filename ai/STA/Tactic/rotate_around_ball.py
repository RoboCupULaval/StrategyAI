# Under MIT licence, see LICENCE.txt

import time
from typing import Optional, List

from Util import Pose
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class RotateAroundBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose, args: Optional[List[str]] = None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.next_position
        self.next_state = self.next_position
        self.target = target
        self.last_time = time.time()

        self.ball_position = self.game_state.ball_position

    def next_position(self):
        return 0

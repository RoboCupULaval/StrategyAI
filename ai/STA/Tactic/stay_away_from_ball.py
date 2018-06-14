# Under MIT license, see LICENSE.txt
from typing import List, Optional

from Util import Pose
from Util.ai_command import MoveTo
from Util.area import stay_outside_circle
from Util.constant import KEEPOUT_DISTANCE_FROM_BALL
from Util.geometry import Area
from ai.GameDomainObjects import Player
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState


class StayAwayFromBall(Tactic):
    def __init__(self, game_state: GameState, player: Player, target: Pose = Pose(),
                 args: Optional[List[str]]=None,
                 keepout_radius: int = KEEPOUT_DISTANCE_FROM_BALL,
                 forbidden_areas: Optional[List[Area]]=None):
        super().__init__(game_state, player, target, args, forbidden_areas=forbidden_areas)
        self.current_state = self.stay_out_of_circle
        self.next_state = self.stay_out_of_circle
        self.keepout_radius = keepout_radius

    def stay_out_of_circle(self):
        position = stay_outside_circle(self.player.pose.position,
                                     self.game_state.ball_position,
                                     self.keepout_radius)
        return MoveTo(Pose(position, self.player.pose.orientation))

from typing import List

from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.geometry import get_distance
from ai.STA.Action.PathfindToPosition import PathfindToPosition
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class VaEtVient(Tactic):
    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None):
        super().__init__(game_state, player, target, args)
        self.start = self.player.pose
        self.end = Pose(position=self.target.position, orientation=0)

    def exec(self):
        if self.check_success():
            self.status_flag = Flags.WIP
            self.switch_target()
        else:
            self.status_flag = Flags.WIP

        return PathfindToPosition(self.game_state, self.player, self.target)

    def switch_target(self):
        player_position = self.player.pose.position
        distance_end = get_distance(player_position, self.end.position)
        distance_start = get_distance(player_position, self.start.position)
        if distance_end < distance_start:
            self.target = self.start
        else:
            self.target = self.end

    def check_success(self):
        player_position = self.player.pose.position

        distance = get_distance(player_position, self.target.position)
        if distance < self.game_state.const["POSITION_DEADZONE"]:
            return True
        return False

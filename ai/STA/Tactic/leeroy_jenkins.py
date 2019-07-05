from typing import List, Optional

from Util import Pose
from Util.ai_command import Idle
from Util.constant import KickForce
from ai.Algorithm.evaluation_module import closest_players_to_point
from ai.GameDomainObjects import Player
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.states.game_state import GameState


class LeeroyJenkins(Tactic):

    MINIMUM_DISTANCE_FOR_SMALL_KICK = 2800

    def __init__(self, game_state: GameState, player: Player, target: Pose = Pose(), args: Optional[List[str]]=None):
        super().__init__(game_state, player, target, args)
        self.go_kick_tactic = None
        self.current_state = self.go_kick_low
        self.next_state = self.go_kick_low

    def go_kick_low(self):
        if self._is_close_enough_from_goal():
            self.go_kick_tactic = None
            self.next_state = self.go_kick_high
            return Idle
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state, self.player, kick_force=KickForce.LOW,
                                         target=self.game_state.field.their_goal_pose)
        if self.go_kick_tactic.status_flag == Flags.SUCCESS:
            self.go_kick_tactic.status_flag = Flags.INIT
        return self.go_kick_tactic.exec()

    def go_kick_high(self):
        if not self._is_close_enough_from_goal():
            self.go_kick_tactic = None
            self.next_state = self.go_kick_low
            return Idle
        if self.go_kick_tactic is None:
            self.go_kick_tactic = GoKick(self.game_state, self.player, kick_force=KickForce.HIGH,
                                         auto_update_target=True)
        if self.go_kick_tactic.status_flag == Flags.SUCCESS:
            self.go_kick_tactic.status_flag = Flags.INIT
        return self.go_kick_tactic.exec()

    def _is_close_enough_from_goal(self):
        if (GameState().field.their_goal_pose - self.game_state.ball_position).norm <= \
               self.MINIMUM_DISTANCE_FOR_SMALL_KICK:
            return True

        closest_enemy = closest_players_to_point(self.game_state.field.their_goal, our_team=False)
        if len(closest_enemy) == 0:
            return False

        goalkeeper = closest_enemy[0].player
        return goalkeeper.position not in self.game_state.field.their_goal_area

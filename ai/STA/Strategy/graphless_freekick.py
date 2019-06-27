# Under MIT License, see LICENSE.txt
import time

import math

from Util import Pose
from Util.constant import ROBOT_RADIUS
from Util.role import Role
from ai.GameDomainObjects import Player
from ai.STA.Strategy.graphless_offense import GraphlessOffense
from ai.STA.Tactic.go_kick import GoKick
from ai.STA.Tactic.go_to_position import GoToPosition
from ai.STA.Tactic.position_for_pass import PositionForPass

TIME_TO_GET_IN_POSITION = 5


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic
class GraphlessFreeKick(GraphlessOffense):

    def __init__(self, p_game_state, can_kick_in_goal):
        super().__init__(p_game_state)
        self.forbidden_areas = [self.game_state.field.free_kick_avoid_area,
                                self.game_state.field.our_goal_forbidden_area]

        self.forbidden_areas_of_position_for_pass = self.forbidden_areas + self.game_state.field.border_limits

        self.ball_start_position = self.game_state.ball.position
        self.can_kick_in_goal = can_kick_in_goal
        self.first_passing_player = None

        self.start_time = time.time()

    def initialize(self):
        self._initialize_tactics()
        self.next_state = self.get_in_position

    def get_in_position(self):
        for role, player in self.assigned_roles.items():
            if role == Role.GOALKEEPER:
                continue
            if self.is_closest_not_goalkeeper(player):
                self.logger.info(f"Robot {player.id} is closest => go behind ball")
                self.first_passing_player = player

                their_goal_to_ball = self.game_state.ball_position - self.game_state.field.their_goal
                go_behind_position = self.game_state.ball_position + their_goal_to_ball.unit * ROBOT_RADIUS * 2.0
                go_behind_orientation = their_goal_to_ball.angle + math.pi
                self.roles_to_tactics[role] = GoToPosition(self.game_state,
                                                           player,
                                                           target=Pose(go_behind_position, go_behind_orientation),
                                                           cruise_speed=1)
            else:
                self.roles_to_tactics[role] = PositionForPass(self.game_state,
                                                              player,
                                                              auto_position=True,
                                                              robots_in_formation=self.robots_in_formation)

        self.next_state = self.wait_before_pass

    def wait_before_pass(self):
        if time.time() - self.start_time > TIME_TO_GET_IN_POSITION:
            self.next_state = self.go_get_ball

    def _will_probably_kick_soon(self, player: Player):
        if self.game_state.double_touch_checker.is_enabled():
            return True
        return super()._will_probably_kick_soon(player)

    def _assign_closest_player_to_gokick(self, player, role):
        if player == self.first_passing_player and self.game_state.double_touch_checker.is_enabled():
            can_kick_in_goal = self.can_kick_in_goal
        else:
            can_kick_in_goal = True

        self.roles_to_tactics[role] = GoKick(self.game_state,
                                             player,
                                             auto_update_target=True,
                                             can_kick_in_goal=can_kick_in_goal,
                                             forbidden_areas=self.forbidden_areas)

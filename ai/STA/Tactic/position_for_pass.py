# Under MIT licence, see LICENCE.txt
import numpy as np
import time
from typing import List, Optional

from Debug.debug_command_factory import DebugCommandFactory, VIOLET, RED
from Util import Pose, Position
from Util.ai_command import CmdBuilder, MoveTo
from Util.geometry import Area, Line, clamp, normalize
from Util.role import Role
from ai.Algorithm.evaluation_module import best_position_in_region
from ai.GameDomainObjects import Player
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

ATTENUATION = 1000 ** 3  # Can be consider the constant that limit the effect of the enemy robot
MIN_DIST_FROM_CENTER = 200  # An enemy player closer than this distance from the area center, its distance will clamp


class PositionForPass(Tactic):
    """
    This tactic automagically positions players at strategic emplacements
    """
    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: Optional[List[str]]=None,
                 auto_position=False, robots_in_formation: Optional[List[Player]] = None):
        super().__init__(game_state, player, target, args)
        self.current_state = self.move_to_pass_position
        self.next_state = self.move_to_pass_position
        self.target = target
        self.auto_position = auto_position
        if robots_in_formation is None:
            self.robots_in_formation = [player]
        else:
            self.robots_in_formation = robots_in_formation

        self.number_of_robots = len(self.robots_in_formation)
        self.is_offense = self.is_player_offense(player)
        self.robots_in_formation = [player for player in self.robots_in_formation if self.is_offense == self.is_player_offense(player)]
        self.idx_in_formation = self.robots_in_formation.index(player)

        # Use for debug_cmd
        self.area = None
        self.best_position = None

    def is_player_offense(self, player):
        role = self.game_state.get_role_by_player_id(player.id)
        return role in [Role.FIRST_ATTACK, Role.SECOND_ATTACK]

    def move_to_pass_position(self):
        destination_orientation = (self.game_state.ball_position - self.player.pose.position).angle

        self.best_position = self._find_best_player_position() if self.auto_position else self.target
        return MoveTo(Pose(self.best_position, destination_orientation))

    def _find_best_player_position(self):
        if not self.auto_position:
            return self.target_position

        if self.is_offense:
            ball_offset = clamp(self.game_state.ball.position.x, 0, 1000)
            left = self.game_state.field.their_goal_area.right + ball_offset
            right = ball_offset
        else:
            ball_offset = clamp(self.game_state.ball.position.x, -1000, 0)
            left = self.game_state.field.our_goal_area.left + ball_offset
            right = ball_offset

        idx = self.robots_in_formation.index(self.player)
        len_formation = len(self.robots_in_formation)

        PADDING = 300  # Add buffer zone between area and the field limit
        area_height = self.game_state.field.field_width - 2 * PADDING

        individual_area_size = area_height / len_formation
        top = idx * individual_area_size - area_height / 2
        bot = top + individual_area_size
        self.area = Area.from_limit(top, bot, left, right)

        center = self.area.center
        # Act as if each enemy robot was creating a repulsive force
        v = Position(0, 0)
        for enemy in self.game_state.enemy_team.available_players.values():
            d = enemy.position - center
            # Clamp distance norm
            d = MIN_DIST_FROM_CENTER * normalize(d) if d.norm < MIN_DIST_FROM_CENTER else d
            # Square of the inverse of the distance, a bit like Newton's law of universal gravitation
            v -= ATTENUATION * d / (d.norm ** 3)
        offset_from_center = Line(center, center + v)

        # The position must stay inside the area limits, so let's find the intersection between our vector and the area
        area_inter = self.area.intersect(offset_from_center)
        if area_inter:
            return area_inter[0]  # First intersection
        return center + v

    def debug_cmd(self):
        if self.area is None:
            return []
        color = VIOLET if self.is_offense else RED
        area_lines = DebugCommandFactory().area(self.area, color=color)
        line_test = DebugCommandFactory().line(self.area.center, self.best_position, color=color)

        return area_lines + [line_test]


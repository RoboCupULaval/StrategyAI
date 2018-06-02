# Under MIT licence, see LICENCE.txt
import numpy as np
import time
from typing import List, Optional

from Debug.debug_command_factory import DebugCommandFactory
from Util import Pose, Position
from Util.ai_command import CmdBuilder, MoveTo
from Util.geometry import Area, Line
from Util.role import Role
from ai.Algorithm.evaluation_module import best_position_in_region
from ai.GameDomainObjects import Player
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.STA.Tactic.tactic import Tactic
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'

DELAY = 1

"""
Tactique qui positionne un joueur à un point donné pour faire face à la balle et peut aussi se positionner 
automatiquement selon son rôle
"""


class PositionForPass(Tactic):

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: Optional[List[str]]=None,
                 auto_position=False, robots_in_formation: Optional[List[Player]] = None):
        super().__init__(game_state, player, target, args)
        self.area = None
        self.current_state = self.move_to_pass_position
        self.next_state = self.move_to_pass_position
        self.auto_position = auto_position
        self.target_position = target
        self.role = self.game_state.get_role_by_player_id(self.player.id)
        if robots_in_formation is None:
            self.robots_in_formation = [player]
        else:
            self.robots_in_formation = robots_in_formation
        self.number_of_robots = len(self.robots_in_formation)
        self.is_offense = self.is_player_offense(player)
        self.robots_in_formation = [player for player in self.robots_in_formation if self.is_offense == self.is_player_offense(player)]
        self.idx_in_formation = self.robots_in_formation.index(player)
        self.target_position = self._find_best_player_position()
        self.last_time = time.time()

    def is_player_offense(self, player):
        role = self.game_state.get_role_by_player_id(player.id)
        return role in [Role.FIRST_ATTACK, Role.SECOND_ATTACK]

    def move_to_pass_position(self):
        self.next_state = self.move_to_pass_position
        return MoveTo(self._get_destination_pose())

    def _get_destination_pose(self):
        # FIXME: There is flag that does not exist anymore and it seem important...
        # if self.player.receiver_pass_flag is False:
        #     self.target_position = self._find_best_player_position()
        self.last_time = time.time()
        destination_orientation = (self.game_state.ball_position - self.player.pose.position).angle
        return Pose(self._find_best_player_position(), destination_orientation)

    def _find_best_player_position(self):
        if not self.auto_position:
            return self.target_position

        idx = self.robots_in_formation.index(self.player)
        len_formation = len(self.robots_in_formation)
        field_width = self.game_state.field.field_width
        if self.is_offense:
            top = idx / len_formation * field_width - field_width / 2
            bot = top + self.game_state.field.field_width / len_formation
            left = self.game_state.field.their_goal_area.right
            right = 0
            self.area = Area.from_limit(top, bot, left, right)
            center = self.area.center
            v = Position(0, 0)

            # Act as if each enemy robot was creating a repulsive force
            ATTENUATION = 1/180**2
            for enemy in self.game_state.enemy_team.available_players.values():
                d = enemy.position - center
                v -= ATTENUATION * d * d.norm  # Double the norm of the vector
            offset_from_center = Line(center, center + v)

            # The position must stay inside the area limits
            area_inter = self.area.intersect(offset_from_center)
            if area_inter:
                return area_inter[0]
            else:
                return center + v
        else:
            return Position(0, 0)  # FIXME


        # pad = 200
        # #if self.game_state.field.our_goal_x > 0:
        # our_goal_field_limit = self.game_state.field.our_goal_x - pad
        # our_side_center_field_limit = pad
        # their_goal_field_limit = GameState().field.their_goal_x + pad
        #     #  their_side_center_field_limit = -pad
        # # else:
        # #     our_goal_field_limit = self.game_state.field.our_goal_x + pad
        # #     our_side_center_field_limit = -pad
        # #     their_goal_field_limit = self.game_state.field.their_goal_x - pad
        # #     #  their_side_center_field_limit = pad
        # field_width = self.game_state.field.field_width
        #
        # self.role = self.game_state.get_role_by_player_id(self.player.id)
        # offense_offset = Position(0, 0)
        # defense_offset = self.compute_defense_offset()
        # if self.role is Role.FIRST_DEFENCE:  # Top defense
        #     A = Position(our_goal_field_limit, self.game_state.field.top + pad) + defense_offset
        #     B = Position(our_side_center_field_limit,
        #                  (self.game_state.field.top - field_width / self.number_of_defense_players) + pad) + defense_offset
        # elif self.role is Role.MIDDLE:  # center
        #     A = Position(our_goal_field_limit + 1000,
        #                  (self.game_state.field.bottom / self.number_of_defense_players) + pad) + defense_offset
        #     B = Position(our_side_center_field_limit,
        #                  self.game_state.field.top / self.number_of_defense_players - pad) + defense_offset
        # elif self.role is Role.SECOND_DEFENCE:  # bottom_defense
        #
        #     A = Position(our_goal_field_limit, pad) + defense_offset
        #     B = Position(our_side_center_field_limit,
        #                  (self.game_state.field.bottom) + field_width / self.number_of_defense_players) + defense_offset
        #
        # elif self.role is Role.FIRST_ATTACK:  # player.role is 'top_offence':
        #     A = Position(their_goal_field_limit, self.game_state.field.top + pad) + offense_offset
        #     B = Position(their_goal_field_limit,
        #                  (self.game_state.field.top - field_width / self.number_of_offense_players) + pad) + offense_offset
        # else:
        #     A = Position(their_goal_field_limit, pad) + offense_offset
        #     B = Position(their_goal_field_limit,
        #                  (self.game_state.field.bottom + field_width / self.number_of_offense_players) - pad) + offense_offset
        # self.area = Area(A, B)
        # return np.array([0, 0])
        # #return best_position_in_region(self.player, A, B)


    def debug_cmd(self):
        if self.area is None:
            return []
        area_lines = DebugCommandFactory().area(self.area)

        line_test = DebugCommandFactory().line(self.area.center, self._find_best_player_position())

        return area_lines + [line_test]


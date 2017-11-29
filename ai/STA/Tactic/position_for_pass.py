# Under MIT licence, see LICENCE.txt
from typing import List
import time

from RULEngine.GameDomainObjects.Player import Player
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.evaluation_module import best_position_in_region
from ai.STA.Tactic.tactic import Tactic
from ai.STA.Tactic.go_to_position_pathfinder import GoToPositionPathfinder
from ai.states.game_state import GameState

from RULEngine.Debug.debug_interface import COLOR_ID_MAP
from ai.Util.role import Role

__author__ = 'RoboCupULaval'

DELAY = 1

"""
Tactique qui positionne un joueur à un point donné pour faire face à la balle et peut aussi se positionner 
automatiquement selon son rôle
"""

class PositionForPass(Tactic):

    def __init__(self, game_state: GameState, player: Player, target: Pose=Pose(), args: List[str]=None,
                 auto_position=False):
        super().__init__(game_state, player, target, args)
        self.current_state = self.move_to_pass_position
        self.next_state = self.move_to_pass_position
        self.auto_position = auto_position
        self.target_position = target
        self.target_position = self._find_best_player_position()
        self.last_time = time.time()

    def move_to_pass_position(self):

        self.next_state = self.move_to_pass_position
        return GoToPositionPathfinder(self.game_state, self.player, self._get_destination_pose())

    def _get_destination_pose(self):
        if self.player.receiver_pass_flag is False:
            self.target_position = self._find_best_player_position()
        self.last_time = time.time()
        destination_orientation = (self.game_state.get_ball_position() - self.player.pose.position).angle()
        return Pose(self.target_position, destination_orientation)

    def _find_best_player_position(self):
        if self.auto_position:
            pad = 200
            if self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] > 0:
                our_goal_field_limit = self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] - pad
                our_side_center_field_limit = pad
                their_goal_field_limit = GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"] + pad
                their_side_center_field_limit = -pad
            else:
                our_goal_field_limit = self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] + pad
                our_side_center_field_limit = -pad
                their_goal_field_limit = self.game_state.const["FIELD_THEIR_GOAL_X_EXTERNAL"] - pad
                their_side_center_field_limit = pad

            role = self.game_state.get_role_by_player_id(self.player.id)
            offense_offset = 0
            defense_offset = self.compute_defense_offset()
            if role is Role.FIRST_DEFENCE:  # role is 'top_defence':
                A = Position(our_goal_field_limit, self.game_state.const["FIELD_Y_TOP"]-pad) + defense_offset
                B = Position(our_side_center_field_limit, (self.game_state.const["FIELD_Y_TOP"] / 3)+pad) + defense_offset
            elif role is Role.SECOND_DEFENCE:  # player.role is 'bottom_defence':
                A = Position(our_goal_field_limit, self.game_state.const["FIELD_Y_BOTTOM"]+pad) + defense_offset
                B = Position(our_side_center_field_limit, (self.game_state.const["FIELD_Y_BOTTOM"] / 3)-pad) + defense_offset
            elif role is Role.FIRST_ATTACK:  # player.role is 'top_offence':
                A = Position(their_goal_field_limit, self.game_state.const["FIELD_Y_BOTTOM"]+pad) + offense_offset
                B = Position(their_side_center_field_limit, pad) + offense_offset
            elif role is Role.SECOND_ATTACK:  # player.role is 'bottom_offence':
                A = Position(their_goal_field_limit, self.game_state.const["FIELD_Y_TOP"]-pad) + offense_offset
                B = Position(their_side_center_field_limit, -pad) + offense_offset
            elif role is Role.MIDDLE:  # player.role is 'center':
                A = Position(our_goal_field_limit+1000, (self.game_state.const["FIELD_Y_BOTTOM"] / 3)+pad) + defense_offset
                B = Position(our_side_center_field_limit, self.game_state.const["FIELD_Y_TOP"] / 3-pad) + defense_offset
            elif role is Role.GOALKEEPER:  # player.role is 'center':
                A = Position(their_goal_field_limit, GameState().const["FIELD_Y_BOTTOM"]+pad)
                B = Position(their_side_center_field_limit, pad)
            return best_position_in_region(self.player, A, B)
        else:
            return self.target_position


    def compute_offence_offset(self):
        if self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] < 0:
            if self.game_state.get_ball_position()[0] < 0:
                offset = Position(self.game_state.get_ball_position()[0] - 1000, 0)
            else:
                offset = Position(0, 0)
        else:
            if self.game_state.get_ball_position()[0] > 0:
                offset = Position(self.game_state.get_ball_position()[0] + 1000, 0)
            else:
                offset = Position(0, 0)
        if abs(offset[0]) > 2000:
            offset[0] = abs(offset[0]) / offset[0] * 2000
        return offset

    def compute_defense_offset(self):
        if GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] < 0:
            if self.game_state.get_ball_position()[0] > 0:
                offset = Position(self.game_state.get_ball_position()[0] - 1000, 0)
            else:
                offset = Position(0, 0)
        else:
            if self.game_state.get_ball_position()[0] < 0:
                offset = Position(self.game_state.get_ball_position()[0] + 1000, 0)
            else:
                offset = Position(0, 0)
        if abs(offset[0]) > 2000:
            offset[0] = abs(offset[0]) / offset[0] * 2000
        return offset

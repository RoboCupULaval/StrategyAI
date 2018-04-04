# Under MIT licence, see LICENCE.txt
import time
from typing import List, Optional

from Util import Pose, Position
from Util.ai_command import CmdBuilder, MoveTo
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
        self.number_of_defence_players = 1
        self.number_of_offense_players = 1
        self.number_of_defence_players = sum(1 for player in self.robots_in_formation if self.is_player_defense(player))
        self.number_of_offense_players = sum(1 for player in self.robots_in_formation if self.is_player_offense(player))
        self.target_position = self._find_best_player_position()
        self.last_time = time.time()

    def is_player_defense(self, player):
        role = self.game_state.get_role_by_player_id(player.id)
        return role is Role.FIRST_DEFENCE or role is Role.SECOND_DEFENCE or role is Role.MIDDLE

    def is_player_offense(self, player):
        role = self.game_state.get_role_by_player_id(player.id)
        return role is Role.FIRST_ATTACK or role is Role.SECOND_ATTACK

    def move_to_pass_position(self):

        self.next_state = self.move_to_pass_position
        return MoveTo(self._get_destination_pose())

    def _get_destination_pose(self):
        # FIXME: There is flag that does not exist anymore and it seem important...
        # if self.player.receiver_pass_flag is False:
        #     self.target_position = self._find_best_player_position()
        self.last_time = time.time()
        destination_orientation = (self.game_state.ball_position - self.player.pose.position).angle
        return Pose(Position.from_array(self.target_position), destination_orientation)

    def _find_best_player_position(self):
        if self.auto_position:

            pad = 200
            if self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] > 0:
                our_goal_field_limit = self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] - pad
                our_side_center_field_limit = pad
                their_goal_field_limit = GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"] + pad
                #  their_side_center_field_limit = -pad
            else:
                our_goal_field_limit = self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] + pad
                our_side_center_field_limit = -pad
                their_goal_field_limit = self.game_state.const["FIELD_THEIR_GOAL_X_EXTERNAL"] - pad
                #  their_side_center_field_limit = pad
            field_width = self.game_state.const["FIELD_Y_TOP"] - self.game_state.const["FIELD_Y_BOTTOM"]

            self.role = self.game_state.get_role_by_player_id(self.player.id)
            offense_offset = self.compute_offence_offset() # FIXME ok?
            defense_offset = self.compute_defense_offset()
            if self.is_player_defense(self.player):  # role is in defense:
                if self.role is Role.FIRST_DEFENCE:
                    A = Position(our_goal_field_limit, self.game_state.const["FIELD_Y_TOP"] + pad) + defense_offset
                    B = Position(our_side_center_field_limit,
                                 (self.game_state.const["FIELD_Y_TOP"] - field_width / self.number_of_defence_players) + pad) + defense_offset
                elif self.role is Role.MIDDLE:  # center
                    A = Position(our_goal_field_limit + 1000,
                                 (self.game_state.const[
                                      "FIELD_Y_BOTTOM"] / self.number_of_defence_players) + pad) + defense_offset
                    B = Position(our_side_center_field_limit,
                                 self.game_state.const[
                                     "FIELD_Y_TOP"] / self.number_of_defence_players - pad) + defense_offset
                else:# bottom_defense

                    A = Position(our_goal_field_limit, pad) + defense_offset
                    B = Position(our_side_center_field_limit,
                                 (self.game_state.const["FIELD_Y_BOTTOM"]) + field_width / self.number_of_defence_players) + defense_offset
            else:
                if self.role is Role.FIRST_ATTACK: # player.role is 'top_offence':
                    A = Position(their_goal_field_limit, self.game_state.const["FIELD_Y_TOP"] + pad) + offense_offset
                    B = Position(their_goal_field_limit,
                                 (self.game_state.const["FIELD_Y_TOP"] - field_width / self.number_of_offense_players) + pad) + offense_offset
                else:
                    A = Position(their_goal_field_limit, pad) + offense_offset
                    B = Position(their_goal_field_limit,
                                 (self.game_state.const["FIELD_Y_BOTTOM"] + field_width / self.number_of_offense_players) - pad) + offense_offset
            return best_position_in_region(self.player, A, B)
        else:
            return self.target_position

    def compute_offence_offset(self):
        if self.game_state.const["FIELD_OUR_GOAL_X_EXTERNAL"] < 0:
            if self.game_state.ball_position[0] < 0:
                offset = Position(self.game_state.ball_position[0] - 1000, 0)
            else:
                offset = Position(0, 0)
        else:
            if self.game_state.ball_position[0] > 0:
                offset = Position(self.game_state.ball_position[0] + 1000, 0)
            else:
                offset = Position(0, 0)
        if abs(offset[0]) > 2000:
            offset[0] = abs(offset[0]) / offset[0] * 2000
        return offset

    def compute_defense_offset(self):
        if GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] < 0:
            if self.game_state.ball_position[0] > 0:
                offset = Position(self.game_state.ball_position[0] - 1000, 0)
            else:
                offset = Position(0, 0)
        else:
            if self.game_state.ball_position[0] < 0:
                offset = Position(self.game_state.ball_position[0] + 1000, 0)
            else:
                offset = Position(0, 0)
        if abs(offset[0]) > 2000:
            offset[0] = abs(offset[0]) / offset[0] * 2000
        return offset

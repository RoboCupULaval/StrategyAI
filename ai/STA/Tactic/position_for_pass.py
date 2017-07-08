# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np
import time

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Algorithm.evaluation_module import best_position_in_region
from ai.STA.Action.AllStar import AllStar
from ai.STA.Tactic.Tactic import Tactic
from ai.Util.ai_command import AICommandType
from ai.states.game_state import GameState
from RULEngine.Debug.debug_interface import COLOR_ID_MAP

__author__ = 'RoboCupULaval'

DELAY = 1

"""
Tactique qui positionne un joueur à un point donné pour faire face à la balle et peut aussi se positionner 
automatiquement selon son rôle
"""

class PositionForPass(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player: Instance du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
        target: Position à laquelle faire face après avoir pris la balle
    """

    def __init__(self, game_state: GameState, player: OurPlayer, target: Pose=Pose(), args: List[str]=None,
                 auto_position=False):
        Tactic.__init__(self, game_state, player, target, args)
        self.current_state = self.move_to_pass_position
        self.next_state = self.move_to_pass_position
        self.auto_position = auto_position
        self.target_position = target
        self.target_position = self._find_best_player_position()
        self.last_time = time.time()

    def move_to_pass_position(self):
        self.next_state = self.move_to_pass_position
        return AllStar(self.game_state, self.player, **{"pose_goal": self._get_destination_pose(),
                                                        "ai_command_type": AICommandType.MOVE})

    def _get_destination_pose(self):
        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y
        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        if time.time() - self.last_time > DELAY:
            self.target_position = self._find_best_player_position()
            self.last_time = time.time()
        destination_orientation = np.arctan2(ball_y - player_y, ball_x - player_x)
        self.game_state.debug_interface.add_point(self.target_position, COLOR_ID_MAP[4], width=5,
                                                  timeout=0.1)
        return Pose(self.target_position, destination_orientation)

    def _find_best_player_position(self):
        if self.auto_position:
            pad = 200
            if GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] > 0:
                our_goal_field_limit = GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] - pad
                our_side_center_field_limit = pad
                their_goal_field_limit = GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"] + pad
                their_side_center_field_limit = -pad
            else:
                our_goal_field_limit = GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"] + pad
                our_side_center_field_limit = -pad
                their_goal_field_limit = GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"] - pad
                their_side_center_field_limit = pad

            if self.player.id == 0:  # role None:
                return Position(0,0)
            elif self.player.id == 1:  # role is 'top_defence':
                A = Position(our_goal_field_limit, GameState().const["FIELD_Y_TOP"]-pad)
                B = Position(our_side_center_field_limit, (GameState().const["FIELD_Y_TOP"] / 3)+pad)
                return best_position_in_region(self.player, A, B)
            elif self.player.id == 2:  # player.role is 'bottom_defence':
                A = Position(our_goal_field_limit, GameState().const["FIELD_Y_BOTTOM"]+pad)
                B = Position(our_side_center_field_limit, (GameState().const["FIELD_Y_BOTTOM"] / 3)-pad)
                return best_position_in_region(self.player, A, B)
            elif self.player.id == 3:  # player.role is 'top_offence':
                A = Position(their_goal_field_limit, GameState().const["FIELD_Y_TOP"]-pad)
                B = Position(their_side_center_field_limit, pad)
                return best_position_in_region(self.player, A, B)
            elif self.player.id == 4:  # player.role is 'bottom_offence':
                A = Position(their_goal_field_limit, GameState().const["FIELD_Y_BOTTOM"]+pad)
                B = Position(their_side_center_field_limit, -pad)
                return best_position_in_region(self.player, A, B)
            elif self.player.id == 5:  # player.role is 'center':
                A = Position(our_goal_field_limit+1000, (GameState().const["FIELD_Y_BOTTOM"] / 3)+pad)
                B = Position(our_side_center_field_limit, GameState().const["FIELD_Y_TOP"] / 3-pad)
                return best_position_in_region(self.player, A, B)
            elif self.player.id == 6:  # role None:
                return Position(0, 0)
        else:
            return self.target_position

# Under MIT licence, see LICENCE.txt
from typing import List
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS, ROBOT_RADIUS
from ai.Algorithm.evaluation_module import best_position_in_region
from ai.STA.Action.AllStar import AllStar
from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.goToPositionPathfinder import GoToPositionPathfinder
from ai.Util.ai_command import AICommandType
from ai.states.game_state import GameState
import time

__author__ = 'RoboCupULaval'

ORIENTATION_DEADZONE = 0.2
DISTANCE_TO_KICK_REAL = ROBOT_RADIUS * 3.4
DISTANCE_TO_KICK_SIM = ROBOT_RADIUS + BALL_RADIUS
COMMAND_DELAY = 1.5


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

    def move_to_pass_position(self):

        self.next_state = self.move_to_pass_position
        # if self._is_player_towards_ball():
        #     self.status_flag = Flags.SUCCESS
        # else:
        #     self.status_flag = Flags.WIP
        # return AllStar(self.game_state, self.player, **{"pose_goal": self._get_destination_pose(),
        #                                                 "ai_command_type": AICommandType.MOVE,
        #                                                 "pathfinder_on": True})
        return GoToPositionPathfinder(self.game_state, self.player, self._get_destination_pose())

    def _is_player_towards_ball(self, fact=-0.99):
        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y
        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        vector_ball_2_player = np.array([player_x - ball_x, player_y - ball_y])
        vector_ball_2_player /= np.linalg.norm(vector_ball_2_player)
        vector_player_dir = np.array([np.cos(self.player.pose.orientation),
                                      np.sin(self.player.pose.orientation)])
        if np.dot(vector_ball_2_player, vector_player_dir) < fact:
            return True
        return False

    def _get_destination_pose(self):

        player_x = self.player.pose.position.x
        player_y = self.player.pose.position.y
        ball_x = self.game_state.get_ball_position().x
        ball_y = self.game_state.get_ball_position().y

        self._find_best_player_position()

        destination_orientation = np.arctan2(ball_y - player_y, ball_x - player_x)

        return Pose(self.target.position, destination_orientation)

    def _find_best_player_position(self):
        if self.auto_position:
            pad = 200
            if self.player.id == 1: #role is 'top_defence':
                A = Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"]+pad, GameState().const["FIELD_Y_TOP"]-pad)
                B = Position(0-pad, (GameState().const["FIELD_Y_TOP"] / 3)+pad)
                self.target.position = best_position_in_region(self.player, A, B)
            elif self.player.id == 2: #player.role is 'bottom_defence':
                A = Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"]+pad, GameState().const["FIELD_Y_BOTTOM"]+pad)
                B = Position(0-pad, (GameState().const["FIELD_Y_BOTTOM"] / 3)-pad)
                self.target.position = best_position_in_region(self.player, A, B)
            elif self.player.id == 3: #player.role is 'top_offence':
                A = Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"]-pad, GameState().const["FIELD_Y_TOP"]-pad)
                B = Position(0+pad, 0+pad)
                self.target.position = best_position_in_region(self.player, A, B)
            elif self.player.id == 4: #player.role is 'bottom_offence':
                A = Position(GameState().const["FIELD_THEIR_GOAL_X_EXTERNAL"]-pad, GameState().const["FIELD_Y_BOTTOM"]+pad)
                B = Position(0+pad, 0-pad)
                self.target.position = best_position_in_region(self.player, A, B)
            elif self.player.id == 5: #player.role is 'center':
                A = Position(GameState().const["FIELD_OUR_GOAL_X_EXTERNAL"]-pad, (GameState().const["FIELD_Y_BOTTOM"] / 3)-pad)
                B = Position(0-pad, GameState().const["FIELD_Y_TOP"] / 3)
                self.target.position = best_position_in_region(self.player, A, B)

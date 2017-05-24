# Under MIT license, see LICENSE.txt
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.game_state import GameState

__author__ = 'Robocup ULaval'


class Grab(Action):
    def __init__(self, game_state: GameState, player: OurPlayer):
        """
            :param game_state: L'etat courant du jeu.
            :param player: Instance du joueur qui se deplace
        """
        Action.__init__(self, game_state, player)

    def exec(self):
        ball = self.game_state.get_ball_position().conv_2_np()
        player = self.player.pose.position.conv_2_np()
        player_to_ball = ball - player
        player_to_ball = 0.3 * player_to_ball / np.linalg.norm(player_to_ball)
        speed_pose = Pose(Position.from_np(player_to_ball))
        self.player.ai_command = AICommand(self.player, AICommandType.MOVE,
                                           **{"pose_goal": speed_pose, "speed_flag": True})
        return self.player.ai_command

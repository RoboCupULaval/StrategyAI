# Under MIT license, see LICENSE.txt
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from ai.STA.Action.Action import Action
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from ai.Util.ai_command import AICommand, AICommandType
from ai.states.game_state import GameState


class Grab(Action):
    """
    Action Move_to: Deplace le robot en vitesse
    Methodes :
        exec(self): Retourne la vitesse en pose
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        speed_pose : Pose representant le vecteur vitesse x,y et la vitesse en orientation du robot
    """
    def __init__(self, game_state: GameState, player: OurPlayer):
        """
            :param game_state: L'etat courant du jeu.
            :param player: Instance du joueur qui se deplace
        """
        Action.__init__(self, game_state, player)

    def exec(self):
        """
        Execute le deplacement
        :return: Un tuple (Pose, kick)
                     ou Pose est la destination du joueur
                        kick est faux (on ne botte pas)
        """
        ball = self.game_state.get_ball_position().conv_2_np()
        player = self.player.pose.position.conv_2_np()
        player_to_ball = ball - player
        player_to_ball = 0.3 * player_to_ball / np.linalg.norm(player_to_ball)
        speed_pose = Pose(Position.from_np(player_to_ball))
        self.player.ai_command = AICommand(self.player, AICommandType.MOVE,
                                           **{"pose_goal": speed_pose, "speed_flag": True})
        return self.player.ai_command

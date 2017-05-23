# Under MIT license, see LICENSE.txt
import numpy as np
from .Action import Action
from RULEngine.Util.constant import PLAYER_PER_TEAM, KICK_MAX_SPD
from ai.Util.ai_command import AICommand, AICommandType
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position

class Kick(Action):
    """
    Action Kick: Actionne le kick du robot
    Méthodes :
        exec(self): Retourne la position actuelle et une force de kick
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur qui doit frapper la balle
    """
    def __init__(self, game_state, p_player_id, p_force, target=Pose()):
        """
            :param game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui frappe la balle
            :param p_force: force du kicker (float entre 0 et 1)
        """
        Action.__init__(self, game_state)
        assert(isinstance(p_player_id, int))
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert(isinstance(p_force, (int, float)))
        assert(KICK_MAX_SPD >= p_force >= 0)
        self.player_id = p_player_id
        self.force = p_force
        self.target = target
        self.speed_pose = Pose()

    def exec(self):
        """
        Execute le kick
        :return: Un tuple (Pose, kick)
                     où Pose est la destination actuelle du joueur (ne pas la modifier)
                        kick est un float entre 0 et 1 qui determine la force du kick
        """
        target = self.target.position.conv_2_np()
        player = self.game_state.game.friends.players[self.player_id].pose.position.conv_2_np()
        player_to_target = target - player
        player_to_target = 0.3 * player_to_target / np.linalg.norm(player_to_target)
        self.speed_pose = Pose(Position.from_np(player_to_target))
        return AICommand(self.player_id, AICommandType.MOVE, **{"pose_goal": self.speed_pose,
                                                                "speed_flag": True,
                                                                "kick": True,
                                                                "kick_strength": self.force})

# Under MIT license, see LICENSE.txt
import numpy as np

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
# FIXME Dubious constant kick max speed
from RULEngine.Util.constant import KICK_MAX_SPD
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType


class Kick(Action):
    """
    Action Kick: Actionne le kick du robot avec un mouvement en avant?
    Méthodes :
        exec(self):
    Attributs (en plus de ceux de Action):

    """
    def __init__(self, game_state: GameState, player: OurPlayer, p_force: [int, float], target: Pose=Pose()):
        """
            :param game_state: L'état courant du jeu.
            :param player: Instance du joueur qui frappe la balle
            :param p_force: force du kicker (float entre 0 et 1)
        """
        # TODO check the force not used by the new interface! MGL 2017/05/23
        Action.__init__(self, game_state, player)
        assert(isinstance(p_force, (int, float)))
        assert(KICK_MAX_SPD >= p_force >= 0)
        self.force = p_force
        self.target = target
        self.speed_pose = Pose()

    def exec(self):
        """
        Execute le kick
        """
        target = self.target.position.conv_2_np()
        player = self.player.pose.position.conv_2_np()
        player_to_target = target - player
        player_to_target = 0.3 * player_to_target / np.linalg.norm(player_to_target)
        self.speed_pose = Pose(Position.from_np(player_to_target))
        self.player.ai_command = AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.speed_pose,
                                                                               "speed_flag": True,
                                                                               "kick": True,
                                                                               "kick_strength": self.force})
        return self.player.ai_command

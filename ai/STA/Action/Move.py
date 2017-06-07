# Under MIT license, see LICENSE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType


class Move(Action):
    """
    Action Move_to: Deplace le robot en vitesse
    Methodes :
        exec(self): Retourne la vitesse en pose
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
        speed_pose : Pose representant le vecteur vitesse x,y et la vitesse en orientation du robot
    """
    def __init__(self, game_state: GameState, player: OurPlayer, speed_pose: Pose):
        """
            :param game_state: L'etat courant du jeu.
            :param player: Instance du joueur qui se deplace
            :param speed_pose: destination (pose) que le joueur doit atteindre
        """
        Action.__init__(self, game_state, player)
        assert isinstance(speed_pose, Pose)
        self.speed_pose = speed_pose

    def exec(self):
        """
        Execute le deplacement
        """
        return AICommand(self.player, AICommandType.MOVE, **{"pose_goal": self.speed_pose, "speed_flag": True})

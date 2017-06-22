# Under MIT licence, see LICENCE.txt
from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle
from ai.states.game_state import GameState
from ai.STA.Action.Action import Action
from ai.Util.ai_command import AICommand, AICommandType

__author__ = 'Robocup ULaval'


class GetBall(Action):
    """
    Action GrabBall: Déplace le robot afin qu'il prenne contrôle de la balle
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    """
    def __init__(self, game_state: GameState, player: OurPlayer):
        """
            :param game_state: L'état courant du jeu.
            :param p_player_id: Identifiant du joueur qui prend le contrôle de la balle
        """
        Action.__init__(self, game_state, player)

    def exec(self):
        """
        Place le robot afin qu'il prenne le contrôle de la balle
        :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
        """
        ball_position = self.game_state.get_ball_position()
        destination_orientation = (ball_position - self.player.pose.position).angle()
        destination_pose = {"pose_goal": Pose(ball_position, destination_orientation)}
        return AICommand(self.player, AICommandType.MOVE, **destination_pose)

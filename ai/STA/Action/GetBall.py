# Under MIT licence, see LICENCE.txt
from Util.ai_command import CmdBuilder
from ai.GameDomainObjects import Player
from Util import AICommand, Pose
from ai.STA.Action import Action
from ai.states.game_state import GameState


class GetBall(Action):
    """
    Action GrabBall: Déplace le robot afin qu'il prenne contrôle de la balle
    Méthodes :
        exec(self): Retourne la pose où se rendre
    Attributs (en plus de ceux de Action):
        player_id : L'identifiant du joueur
    """
    def __init__(self, game_state: GameState, player: Player):
        """
            :param game_state: L'état courant du jeu.
            :param player: Joueur qui prend le contrôle de la balle
        """
        Action.__init__(self, game_state, player)

    def exec(self):
        """
        Place le robot afin qu'il prenne le contrôle de la balle
        :return: Un tuple (Pose, kick) où Pose est la destination du joueur et kick est nul (on ne botte pas)
        """
        ball_position = self.game_state.get_ball_position()
        destination_orientation = (ball_position - self.player.pose.position).angle

        return CmdBuilder().addMoveTo(Pose(ball_position, destination_orientation)).build()

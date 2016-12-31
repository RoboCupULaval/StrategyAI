# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.MoveToPosition import MoveToPosition
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic import tactic_constants
from ai.Util.ball_possession import hasBallFacingTarget
from ai.STA.Tactic.tactic_constants import Flags
from ai.Util.ball_possession import hasBall
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.constant import PLAYER_PER_TEAM

__author__ = 'RoboCupULaval'


class ReceiveBall(Tactic):
    # TODO : Ajouter un état permettant de faire une translation pour attraper la balle si celle-ci se dirige à côté
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        game_state: L'état courant du jeu.
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
    """

    def __init__(self, game_state, player_id):
        Tactic.__init__(self, game_state, player_id)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.rotate_towards_ball
        self.next_state = self.rotate_towards_ball
        self.player_id = player_id

    def rotate_towards_ball(self):
        if hasBallFacingTarget(self.game_state, self.player_id, point=self.game_state.get_ball_position()):
            self.next_state = self.halt
            self.status_flag = Flags.SUCCESS
            return Idle(self.game_state, self.player_id)
        else:  # keep rotating
            current_position = self.game_state.get_player_position()
            ball_position = self.game_state.get_ball_position()

            rotation_towards_ball = get_angle(current_position, ball_position)
            pose_towards_ball = Pose(current_position, rotation_towards_ball)

            move_to = MoveToPosition(self.game_state, self.player_id, pose_towards_ball)
            self.next_state = self.rotate_towards_ball
            self.status_flag = Flags.WIP
            return move_to

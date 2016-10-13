# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic import tactic_constants
from RULEngine.Util.area import player_close_to_ball_facing_target
from RULEngine.Util.Pose import Pose
from RULEngine.Util.geometry import get_angle
from RULEngine.Util.constant import PLAYER_PER_TEAM

__author__ = 'RoboCupULaval'


class ReceivePass(Tactic):
    # TODO : Ajouter un état permettant de faire une translation pour attraper la balle si celle-ci se dirige à côté
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
    """

    def __init__(self, game_state, player_id):
        Tactic.__init__(self, game_state)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.rotate_towards_ball
        self.next_state = self.rotate_towards_ball
        self.player_id = player_id

    def rotate_towards_ball(self):
        if player_grabbed_ball(self.game_state, self.player_id):
            self.next_state = self.halt
            self.status_flag = tactic_constants.SUCCESS
            return Idle(self.game_state, self.player_id)
        else:  # keep rotating
            current_position = self.game_state.get_player_position()
            ball_position = self.game_state.get_ball_position()

            rotation_towards_ball = get_angle(current_position, ball_position)
            pose_towards_ball = Pose(current_position, rotation_towards_ball)

            move_to = MoveTo(self.game_state, self.player_id, pose_towards_ball)
            self.next_state = self.rotate_towards_ball
            self.status_flag = tactic_constants.WIP
            return move_to

# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action import MoveTo, Idle
from RULEngine.Util.area import player_grabbed_ball
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
    """

    def __init__(self, info_manager, player_id):
        Tactic.__init__(self, info_manager)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0

        self.current_state = self.rotate_towards_ball
        self.next_state = self.rotate_towards_ball
        self.player_id = player_id

    def rotate_towards_ball(self):
        if player_grabbed_ball(self.info_manager, self.player_id):
            self.next_state = self.halt
            return Idle(self.info_manager, self.player_id)
        else:  # keep rotating
            current_position = self.info_manager.get_player_position()
            ball_position = self.info_manager.get_ball_position()

            rotation_towards_ball = get_angle(current_position,ball_position)
            pose_towards_ball = Pose(current_position,rotation_towards_ball)

            move_to = MoveTo(self.info_manager,self.player_id,pose_towards_ball)
            self.next_state = self.rotate_towards_ball
            return move_to

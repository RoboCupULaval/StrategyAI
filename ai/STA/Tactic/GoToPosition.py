# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic import Tactic
from ai.STA.Action.MoveTo import MoveTo
from RULEngine.Util.geometry import get_distance, get_angle
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import ANGLE_TO_HALT, POSITION_DEADZONE, PLAYER_PER_TEAM

__author__ = 'RoboCupULaval'


class GoToPosition(Tactic):
    # TODO : Renommer la classe pour illustrer le fait qu'elle set une Pose et non juste une Position
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur auquel est assigné la tactique
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        destination_pose : La pose de destination du robot
    """

    def __init__(self, info_manager, player_id, destination_pose):
        Tactic.__init__(self, info_manager)
        assert isinstance(player_id, int)
        assert PLAYER_PER_TEAM >= player_id >= 0
        assert isinstance(destination_pose, Pose)

        self.current_state = self.move_to_position
        self.next_state = self.move_to_position
        self.player_id = player_id
        self.destination_pose = destination_pose

    def move_to_position(self):
        player_position = self.info_manager.get_player_position(self.player_id)
        player_orientation = self.info_manager.get_player_orientation(self.player_id)

        if get_distance(player_position, self.destination_pose.position) <= POSITION_DEADZONE or \
                get_angle(player_orientation, self.destination_pose.orientation) <= ANGLE_TO_HALT:
                self.next_state = self.halt
        else:
            self.next_state = self.move_to_position

        return MoveTo(self.info_manager, self.player_id, self.destination_pose)

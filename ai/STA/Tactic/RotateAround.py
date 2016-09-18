
# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.GrabBall import GrabBall
from ai.STA.Action.Kick import Kick
from ai.STA.Action.Idle import Idle
from ai.STA.Tactic import tactic_constants
from RULEngine.Util.area import player_close_to_ball_facing_target, player_can_grab_ball
from RULEngine.Util.geometry import rotate_point_around_origin, get_required_kick_force, get_distance, get_angle
from RULEngine.Util.constant import PLAYER_PER_TEAM, FIELD_X_LEFT, FIELD_X_RIGHT, RADIUS_TO_HALT
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
import math

__author__ = 'RoboCupULaval'


class RotateAround(Tactic):
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
        self.current_state = self.checkit
        self.next_state = self.checkit
        self.player_id = player_id
        self.player_target = self.info_manager.get_player_target(self.player_id)

    def checkit(self):
        if player_close_to_ball_facing_target(self.info_manager, self.player_id):
            self.status_flag = tactic_constants.SUCCESS
            self.next_state = self.halt
            return Idle(self.info_manager, self.player_id)
        else:
            robot_pos = self.info_manager.get_player_position(self.player_id)
            target_pos = self.player_target

            # check if counter clockwise
            constant_angle_increment = 1
            if get_angle(robot_pos, target_pos) < 0:
                constant_angle_increment *= -1

            # calculate new pose
            new_position = rotate_point_around_origin(robot_pos, target_pos, constant_angle_increment)
            new_orientation = get_angle(new_position, target_pos)
            new_pose = Pose(new_position, new_orientation)

            # return command
            self.next_state = self.checkit
            self.status_flag = tactic_constants.WIP
            go_to_position = MoveTo(self.info_manager, self.player_id, new_pose)
            return go_to_position



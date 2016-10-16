# Under MIT licence, see LICENCE.txt

from ai.STA.Tactic.Tactic import Tactic
from ai.STA.Tactic.tactic_constants import Flags
from ai.STA.Action.GoBetween import GoBetween
from ai.STA.Action.MoveTo import MoveTo
from ai.STA.Action.Idle import Idle
from RULEngine.Util.area import isInsideSquare, stayInsideSquare, stayOutsideGoalArea
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import PLAYER_PER_TEAM, ROBOT_RADIUS
from RULEngine.Util.geometry import get_angle

__author__ = 'RoboCupULaval'


class CoverZone(Tactic):
    """
    méthodes:
        exec(self) : Exécute une Action selon l'état courant
    attributs:
        info_manager: référence à la façade InfoManager
        player_id : Identifiant du joueur à qui la tactique est assignée
        y_top : La limite supérieur de la zone
        y_bottom : La limite inférieur de la zone
        x_left : La limite de gauche de la zone
        x_right : La limite de droite de la zone
        is_yellow : Un booléen indiquant si le joueur fait parti de l'équipe des jaunes, dont la zone défensive est la
        moitié droite du terrain.
        current_state : L'état courant de la tactique
        next_state : L'état suivant de la tactique
        status_flag : L'indicateur de progression de la tactique
    """

    def __init__(self, p_game_state, p_player_id, p_y_top, p_y_bottom, p_x_left, p_x_right, p_is_yellow=False):
        Tactic.__init__(self, p_game_state, p_player_id)
        assert isinstance(p_player_id, int)
        assert PLAYER_PER_TEAM >= p_player_id >= 0
        assert isinstance(p_y_top, (int, float))
        assert isinstance(p_y_bottom, (int, float))
        assert isinstance(p_x_left, (int, float))
        assert isinstance(p_x_right, (int, float))
        assert isinstance(p_is_yellow, bool)

        self.player_id = p_player_id
        self.y_top = p_y_top
        self.y_bottom = p_y_bottom
        self.x_left = p_x_left
        self.x_right = p_x_right
        self.is_yellow = p_is_yellow
        self.current_state = self.cover_zone
        self.next_state = self.cover_zone
        self.status_flag = Flags.WIP
        self.target = Pose(Position(int((p_x_right - p_x_left)/2), int((p_y_top - p_y_bottom)/2)))

    def cover_zone(self):
        enemy_positions = self.get_enemy_in_zone()
        ball_pos = self.game_state.get_ball_position()

        if len(enemy_positions) == 0:
            self.next_state = self.support_other_zone
            return Idle(self.game_state, self.player_id)
        else:
            self.next_state = self.cover_zone

        mean_position = Position()
        for pos in enemy_positions:
            mean_position = mean_position + pos
        mean_position /= len(enemy_positions)
        destination = stayInsideSquare(mean_position, self.y_top, self.y_bottom, self.x_left, self.x_right)
        return GoBetween(self.game_state, self.player_id, ball_pos, destination, 2*ROBOT_RADIUS)

    def support_other_zone(self):
        enemy_positions = self.get_enemy_in_zone()

        if len(enemy_positions) == 0:
            self.next_state = self.support_other_zone
        else:
            self.next_state = self.cover_zone

        destination = stayInsideSquare(self.game_state.get_ball_position(), self.y_top, self.y_bottom, self.x_left,
                                       self.x_right)
        destination = stayOutsideGoalArea(destination, self.is_yellow)
        orientation = get_angle(destination, self.game_state.get_ball_position())
        return MoveTo(self.game_state, self.player_id, Pose(destination, orientation))

    def get_enemy_in_zone(self):
        enemy_list = []
        for robot in range(6):
            pos = self.game_state.get_player_pose(robot, False).position
            if isInsideSquare(pos, self.y_top, self.y_bottom, self.x_left, self.x_right):
                enemy_list.append(pos)
        return enemy_list

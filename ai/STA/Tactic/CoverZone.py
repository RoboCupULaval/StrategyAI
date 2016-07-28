from .Tactic import Tactic
from RULEngine.Util.area import isInsideSquare
from RULEngine.Util.Position import Position

__author__ = 'RoboCupULaval'


class CoverZone(Tactic):
    """

    """

    def __init__(self, p_info_manager, p_player_id, p_y_top, p_y_bottom, p_x_left, p_x_right):
        Tactic.__init__(self, p_info_manager)
        assert isinstance(p_player_id, int)
        assert isinstance(p_y_top, (int, float))
        assert isinstance(p_y_bottom, (int, float))
        assert isinstance(p_x_left, (int, float))
        assert isinstance(p_x_right, (int, float))

        self.player_id = p_player_id
        self.y_top = p_y_top
        self.y_bottom = p_y_bottom
        self.x_left = p_x_left
        self.x_right = p_x_right
        self.current_state = None
        self.next_state = None

    def cover_zone(self):
        enemy_positions = self.get_enemy_in_zone()

        if len(enemy_positions) == 0:
            self.next_state = self.support_other_zone
        else:
            self.next_state = self.cover_zone

        mean_position = Position()
        for pos in enemy_positions:
            mean_position = mean_position + pos
        mean_position = mean_position / len(enemy_positions)


    def go_to_center(self):
        pass

    def support_other_zone(self):
        pass

    def get_enemy_in_zone(self):
        enemy_list = []
        for robot in self.info_manager.enemy:
            if isInsideSquare(robot['position'], self.y_top, self.y_bottom, self.x_left, self.x_right):
                enemy_list.append(robot['position'])
        return enemy_list

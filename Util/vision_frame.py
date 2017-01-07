from RULEngine.Util.Position import Position


class VisionFrame(object):

    def __init__(self):
        self.blue_team = {}
        self.yellow_team = {}
        self.ball = None

    def set_ball_position(self, new_ball_position):
        assert isinstance(new_ball_position, Position)

        self.ball = new_ball_position

    def set_blue_player(self, robot_id, new_player_position):
        assert isinstance(robot_id, int)
        assert isinstance(new_player_position, Position)

        self.blue_team[robot_id] = new_player_position

    def set_yellow_player(self, robot_id, new_player_position):
        assert isinstance(robot_id, int)
        assert isinstance(new_player_position, Position)

        self.blue_team[robot_id] = new_player_position


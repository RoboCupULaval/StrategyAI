# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.RotateAround import RotateAround
from ai.STA.Tactic.Stop import Stop
from . Strategy import Strategy
from RULEngine.Util.Position import Position
from RULEngine.Util.area import player_grabbed_ball

class TestingStrategy(Strategy):
    def __init__(self, p_info_manager):

        self.info_manager = p_info_manager

        self.tactics = []
        for i in range(0,5):
            self.tactics.append(Stop(self.info_manager, i))

        self.update_test()

        super().__init__(self.info_manager, self.tactics)

    def update_test(self):

        self.test_robot = 1 ### select robot here

        ### select test here:

        #self.test_go_get_ball()
        self.test_go_rotate_around_ball()

    def test_go_get_ball(self):
        self.tactics[self.test_robot] = GoGetBall(self.info_manager, self.test_robot)

    def test_go_rotate_around_ball(self):
        test_target = Position(1500,-1500)
        if player_grabbed_ball(self.info_manager, self.test_robot):
            self.info_manager.set_player_target(self.test_robot, test_target)
            ball_pos = self.info_manager.get_ball_position()
            self.tactics[self.test_robot] = RotateAround(self.info_manager, self.test_robot, ball_pos)
        else:
            self.tactics[self.test_robot] = GoGetBall(self.info_manager, self.test_robot)
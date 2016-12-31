# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.RotateAround import RotateAround
from ai.STA.Tactic.Stop import Stop
from . Strategy import Strategy
from RULEngine.Util.Position import Position
from RULEngine.Util.area import hasBall

class TestingStrategy(Strategy):
    def __init__(self, p_info_manager):

        self.info_manager = p_info_manager

        self.tactics = []
        for i in range(0,5):
            self.tactics.append(Stop(self.info_manager, i))


        self.update_test()

        super().__init__(self.info_manager, self.tactics)

    def update_test(self):

        ### select robot and target here:

        self.test_robot = 1
        self.test_target = Position(500,1500)
        self.info_manager.set_player_target(self.test_robot, self.test_target)

        ### select test here:

        #self.test_go_get_ball()
        #self.test_go_rotate_around_ball()
        self.rotate_around_random_point()

    def test_go_get_ball(self):
        self.tactics[self.test_robot] = GoGetBall(self.info_manager, self.test_robot)

    def test_go_rotate_around_ball(self):
        if hasBall(self.info_manager, self.test_robot):
            self.tactics[self.test_robot] = rotate_around(self.info_manager, self.test_robot)
        else:
            self.tactics[self.test_robot] = GoGetBall(self.info_manager, self.test_robot)

    def rotate_around_random_point(self):
        phony_origin = self.info_manager.get_ball_position()#Position(-1500,0)
        self.tactics[self.test_robot] = rotate_around(self.info_manager, self.test_robot, phony_origin)
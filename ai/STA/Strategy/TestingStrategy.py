# Under MIT license, see LICENSE.txt

from ai.STA.Tactic.GoGetBall import GoGetBall
from ai.STA.Tactic.Stop import Stop
from . Strategy import Strategy

class TestingStrategy(Strategy):
    def __init__(self, p_info_manager):

        self.info_manager = p_info_manager

        self.tactics =   [Stop(self.info_manager, 0),
                          Stop(self.info_manager, 1),
                          Stop(self.info_manager, 2),
                         Stop(self.info_manager, 3),
                         Stop(self.info_manager, 4),
                         Stop(self.info_manager, 5)]

        self.test_robot = 4
        self.update_test()

        super().__init__(self.info_manager, self.tactics)

    def update_test(self):
        self.test_go_get_ball()
        #test2

    def test_go_get_ball(self):
        self.tactics[self.test_robot] = GoGetBall(self.info_manager, self.test_robot)
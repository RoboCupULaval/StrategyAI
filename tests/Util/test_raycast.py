# Under MIT licence, see LICENCE.txt

import unittest
from math import pi

from RULEngine.Game.Ball import Ball
from RULEngine.Util.Position import Position
from RULEngine.Util.constant import BALL_RADIUS
from ai.Util.Raycast import *

__author__ = 'RoboCupULaval'


# TODO : Tester de façon plus exhaustive
class TestRaycast(unittest.TestCase):
    def setUp(self):
        self.info_manager = InfoManager()
        self.ball = Ball()
        self.ball.set_position(Position(100, 0), 1)
        self.info_manager._update_ball(self.ball)

    def test_raycast(self):
        self.assertTrue(raycast(self.info_manager, Position(100, 100), 200, -pi/2, BALL_RADIUS, [], [], False))

    def test_raycast2(self):
        pass

if __name__ == "__main__":
    unittest.main()

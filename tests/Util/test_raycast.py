# Under MIT licence, see LICENCE.txt

import unittest
from math import pi

from ai.Util.Raycast import *
from ai.states.game_state import GameState

__author__ = 'RoboCupULaval'


# TODO : Tester de façon plus exhaustive
class TestRaycast(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.game_state._update_ball_position(Position(100, 0))

    def test_raycast(self):
        self.assertTrue(raycast(self.game_state, Position(100, 100), 200, -pi/2, BALL_RADIUS, [], [], False))

    def test_raycast2(self):
        pass

if __name__ == "__main__":
    unittest.main()

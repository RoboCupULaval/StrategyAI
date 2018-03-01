import unittest

from ai.states.world_state import WorldState
from ai.executors.motion_executor import RobotMotion
from RULEngine.Util.Position import Position
from RULEngine.Game.OurPlayer import OurPlayer


class TestRobotMotion(unittest.TestCase):

    def setUp(self):
        self.ws = WorldState()
        self.rm = RobotMotion(self.ws, 0)
        self.rm.setting.rotation.deadzone = 0.1
        self.rm.setting.rotation.sensibility = 0.01
        self.rm.setting.rotation.max_speed = 1
        self.rm.setting.translation.deadzone = 0.1
        self.rm.setting.translation.sensibility = 0.01
        self.rm.setting.translation.max_speed = 2
        self.rm.setting.translation.max_acc = 2
        self.rm.dt = 0.05

    def test_limit_speed(self):
        self.assertEqual(self.rm.limit_speed(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_speed(Position(0.5, 0.5)), Position(0.5, 0.5))
        self.assertEqual(self.rm.limit_speed(Position(1.0, 1.0)), Position(1.0, 1.0))
        self.assertEqual(self.rm.limit_speed(Position(2.0, 2.0)), Position(1.414, 1.414))

        self.assertEqual(self.rm.limit_speed(Position(-0.5, -0.5)), Position(-0.5, -0.5))
        self.assertEqual(self.rm.limit_speed(Position(-1.0, -1.0)), Position(-1.0, -1.0))
        self.assertEqual(self.rm.limit_speed(Position(-2.0, -2.0)), Position(-1.414, -1.414))

        self.assertEqual(self.rm.limit_speed(Position(0.5, -0.5)), Position(0.5, -0.5))
        self.assertEqual(self.rm.limit_speed(Position(1.0, -1.0)), Position(1.0, -1.0))
        self.assertEqual(self.rm.limit_speed(Position(2.0, -2.0)), Position(1.414, -1.414))

        self.assertEqual(self.rm.limit_speed(Position(-0.5, 0)), Position(-0.5, 0.0))
        self.assertEqual(self.rm.limit_speed(Position(-1.0, 0)), Position(-1.0, 0.0))
        self.assertEqual(self.rm.limit_speed(Position(-2.0, 0)), Position(-2.0, 0.0))
        self.assertEqual(self.rm.limit_speed(Position(-3.0, 0)), Position(-2.0, 0.0))

    def test_target_reached(self):
        self.rm.target_speed = 1
        self.rm.cruise_speed = 2

        self.rm.position_error = Position(0, 0)
        self.assertTrue(self.rm.target_reached())

        self.rm.position_error = Position(0, OurPlayer.max_acc)
        self.assertFalse(self.rm.target_reached())

        self.rm.position_error = Position(OurPlayer.max_acc,  OurPlayer.max_acc)
        self.assertFalse(self.rm.target_reached(boost_factor=0.5))

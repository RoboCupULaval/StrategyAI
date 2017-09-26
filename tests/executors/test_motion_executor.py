import unittest

import math as m

from ai.states.world_state import WorldState
from ai.executors.motion_executor import RobotMotion
from RULEngine.Util.Position import Position
from config.config_service import ConfigService
from RULEngine.Game.OurPlayer import OurPlayer


class TestRobotMotion(unittest.TestCase):

    def setUp(self):
        ConfigService().load_file('../../config/sim.cfg')
        self.ws = WorldState()
        self.rm = RobotMotion(self.ws, 0)
        self.rm.setting.rotation.deadzone = 0.1
        self.rm.setting.rotation.sensibility = 0.01
        self.rm.setting.rotation.max_speed = OurPlayer.max_angular_speed
        self.rm.setting.translation.deadzone = 0.1
        self.rm.setting.translation.sensibility = 0.01
        self.rm.setting.translation.max_speed = OurPlayer.max_speed
        self.rm.setting.translation.max_acc = OurPlayer.max_acc
        self.rm.dt = 0.05

    def test_apply_rotation_constraints(self):
        self.assertEqual(self.rm.apply_rotation_constraints(0), 0)
        self.assertEqual(self.rm.apply_rotation_constraints(0.001), 0)
        self.assertEqual(self.rm.apply_rotation_constraints(0.00999), 0)
        self.assertEqual(self.rm.apply_rotation_constraints(0.01), 0.1)
        self.assertEqual(self.rm.apply_rotation_constraints(0.1), 0.1)
        self.assertEqual(self.rm.apply_rotation_constraints(0.5), 0.5)
        self.assertEqual(self.rm.apply_rotation_constraints(1), 1)
        self.assertEqual(self.rm.apply_rotation_constraints(OurPlayer.max_angular_speed), OurPlayer.max_angular_speed)
        self.assertEqual(self.rm.apply_rotation_constraints(OurPlayer.max_angular_speed+1), OurPlayer.max_angular_speed)

        self.assertEqual(self.rm.apply_rotation_constraints(-0.001), 0)
        self.assertEqual(self.rm.apply_rotation_constraints(-0.00999), 0)
        self.assertEqual(self.rm.apply_rotation_constraints(-0.01), -0.1)
        self.assertEqual(self.rm.apply_rotation_constraints(-0.1), -0.1)
        self.assertEqual(self.rm.apply_rotation_constraints(-0.5), -0.5)
        self.assertEqual(self.rm.apply_rotation_constraints(-1), -1)
        self.assertEqual(self.rm.apply_rotation_constraints(
                         -OurPlayer.max_angular_speed),
                         -OurPlayer.max_angular_speed)
        self.assertEqual(self.rm.apply_rotation_constraints(
                         -OurPlayer.max_angular_speed-1),
                         -OurPlayer.max_angular_speed)

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

    def test_limit_acceleration(self):
        # test only +x component
        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(
                         Position(self.rm.dt*OurPlayer.max_acc, 0)),
                         Position(self.rm.dt*OurPlayer.max_acc, 0))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(self.rm.dt*OurPlayer.max_acc, 0)), Position(self.rm.dt*OurPlayer.max_acc, 0))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(1.1*self.rm.dt*OurPlayer.max_acc, 0)), Position(self.rm.dt*OurPlayer.max_acc, 0))
        self.rm.stop()

        # test only -x component
        self.assertEqual(self.rm.limit_acceleration(-Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(
                         Position(-0.5*self.rm.dt*OurPlayer.max_acc, 0)),
                         Position(-0.5*self.rm.dt*OurPlayer.max_acc, 0))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(-Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(-Position(self.rm.dt*OurPlayer.max_acc, 0)), -Position(self.rm.dt*OurPlayer.max_acc, 0))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(-Position(0, 0)), -Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(-Position(1.1*self.rm.dt*OurPlayer.max_acc, 0)), -Position(self.rm.dt*OurPlayer.max_acc, 0))
        self.rm.stop()

        # test only +y component
        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(
                         Position(0, 0.5*self.rm.dt*OurPlayer.max_acc)),
                         Position(0, 0.5*self.rm.dt*OurPlayer.max_acc))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(0, self.rm.dt*OurPlayer.max_acc)), Position(0, self.rm.dt*OurPlayer.max_acc))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(0, 1.1*self.rm.dt*OurPlayer.max_acc)), Position(0, self.rm.dt*OurPlayer.max_acc))
        self.rm.stop()

        # test only -y component
        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(
                         Position(0, -0.5*self.rm.dt*OurPlayer.max_acc)),
                         Position(0, -0.5*self.rm.dt*OurPlayer.max_acc))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(0, -self.rm.dt*OurPlayer.max_acc)), Position(0, -self.rm.dt*OurPlayer.max_acc))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(0, -1.1*self.rm.dt*OurPlayer.max_acc)), Position(0, -self.rm.dt*OurPlayer.max_acc))
        self.rm.stop()

        # test x-y components
        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(
                         Position(self.rm.dt*OurPlayer.max_acc, self.rm.dt*OurPlayer.max_acc)),
                         Position(self.rm.dt*OurPlayer.max_acc, self.rm.dt*OurPlayer.max_acc) / m.sqrt(2))
        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(
                         Position(self.rm.dt*OurPlayer.max_acc, -self.rm.dt*OurPlayer.max_acc)),
                         Position(self.rm.dt*OurPlayer.max_acc, -self.rm.dt*OurPlayer.max_acc) / m.sqrt(2))
        self.rm.stop()

        # test multiple speed command

        speed = OurPlayer.max_acc * self.rm.dt

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(0, speed)), Position(0, speed))
        self.assertEqual(self.rm.limit_acceleration(Position(speed, speed)), Position(speed, speed))
        self.assertEqual(self.rm.limit_acceleration(Position(0, speed)), Position(0, speed))
        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.rm.stop()

        speed_list = [(0, 0), (1, 1), (1.5, 1.5), (2, 2), (4, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8),
                      (8, 8), (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (0,0)]

        for test_speed, excepted_speed in speed_list:
            self.assertEqual(self.rm.limit_acceleration(Position(0, test_speed * speed)),
                                                        Position(0, excepted_speed * speed))

        self.rm.stop()

        self.assertEqual(self.rm.limit_acceleration(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.limit_acceleration(Position(0 * speed, 1 * speed)),
                                                    Position(0 * speed, 1 * speed))
        self.assertEqual(self.rm.limit_acceleration(Position(1 * speed, 0 * speed)),
                                                    Position(speed * 1/m.sqrt(2), speed * (1 - 1/m.sqrt(2))))
        self.assertEqual(self.rm.limit_acceleration(Position(1 * speed, 0 * speed)),
                                                    Position(1 * speed, 0))
        self.rm.stop()

    def test_apply_translation_constraints(self):
        deadzone = self.rm.setting.translation.deadzone
        self.assertEqual(self.rm.apply_translation_constraints(Position(0, 0)), Position(0, 0))
        self.assertEqual(self.rm.apply_translation_constraints(Position(-deadzone, 0)), Position(-deadzone, 0))
        self.rm.stop()
        self.assertEqual(self.rm.apply_translation_constraints(Position(deadzone, 0)), Position(deadzone, 0))
        self.rm.stop()
        self.assertEqual(self.rm.apply_translation_constraints(Position(0, -deadzone)), Position(0, -deadzone))
        self.rm.stop()

    def test_target_reached(self):
        self.rm.target_speed = 1
        self.rm.cruise_speed = 2

        self.rm.position_error = [0, 0]
        self.assertTrue(self.rm.target_reached())

        self.rm.position_error = [0, OurPlayer.max_acc]
        self.assertTrue(self.rm.target_reached())

        self.rm.position_error = [OurPlayer.max_acc, 0]
        self.assertTrue(self.rm.target_reached())

        self.rm.position_error = [OurPlayer.max_acc,  OurPlayer.max_acc]
        self.assertTrue(self.rm.target_reached())
        self.assertFalse(self.rm.target_reached(boost_factor=0.5))

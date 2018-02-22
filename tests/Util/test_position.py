import math as m
import unittest

import numpy as np

from Util import Position
from Util.position import normalized, perpendicular, rotate, is_close


class TestPosition(unittest.TestCase):

    def test_new_without_args(self):
        self.assertEqual(Position(), Position(0, 0))

    def test_attributes(self):
        self.assertTrue(hasattr(Position(), 'x'))
        self.assertTrue(hasattr(Position(), 'y'))

    def test_get_x(self):
        pos = Position(1, 2)
        self.assertTrue(pos.x == 1)

    def test_get_y(self):
        pos = Position(1, 2)
        self.assertTrue(pos.y == 2)

    def test_set_x(self):
        pos = Position(1, 2)
        pos.x = 4
        self.assertTrue(pos.x == 4)

    def test_set_y(self):
        pos = Position(1, 2)
        pos.y = 4
        self.assertTrue(pos.y == 4)

    def test_new_with_null_args(self):
        pos = Position(0, 0)
        self.assertEqual(pos.x, 0)
        self.assertEqual(pos.y, 0)

    def test_new_with_real_args(self):
        pos = Position(-100, 0.001)
        self.assertEqual(pos.x, -100)
        self.assertEqual(pos.y, 0.001)

    def test_from_array(self):
        my_array = np.array([100, -50.23])
        pos = Position.from_array(my_array)
        self.assertEqual(pos.x, 100)
        self.assertEqual(pos.y, -50.23)

    def test_from_array_is_not_same(self):
        my_array = np.array([100, -50.23])
        pos = Position.from_array(my_array)
        my_array[0] = 10
        self.assertNotEqual(pos.x, 10)

    def test_from_list(self):
        pos = Position.from_list([100, -50.23])
        self.assertEqual(pos.x, 100)
        self.assertEqual(pos.y, -50.23)

    def test_from_dict(self):
        test_dict = {'x': -1.23, 'y': 4.56}
        pos = Position.from_dict(test_dict)
        self.assertEqual(pos.x, -1.23)
        self.assertEqual(pos.y, 4.56)

    def test_equal_zero(self):
        pos1 = Position()
        pos2 = Position()
        self.assertTrue(pos1 == pos2)

    def test_equal_real_args(self):
        pos1 = Position(500, 549)
        pos2 = Position(400, -400)
        self.assertFalse(pos1 == pos2)

    def test_not_equal(self):
        pos1 = Position(500, 549)
        pos2 = Position(400, -400)
        self.assertTrue(pos1 != pos2)

    def test_angle(self):
        test_angle = 10 * np.pi/180
        pos = Position(m.cos(test_angle), m.sin(test_angle))
        self.assertEqual(pos.angle, test_angle)

    def test_angle_at_zero(self):
        test_angle = 0 * np.pi/180
        pos = Position(m.cos(test_angle), m.sin(test_angle))
        self.assertEqual(pos.angle, test_angle)

    def test_angle_at_180(self):
        test_angle = 180 * np.pi/180
        pos = Position(m.cos(test_angle), m.sin(test_angle))
        self.assertEqual(pos.angle, test_angle)

    def test_norm_with_null_position(self):
        pos = Position()
        self.assertEqual(pos.norm, 0)

    def test_norm_with_real_args(self):
        self.assertEqual(Position(1, 1).norm, m.sqrt(2))

    def test_norm_with_negative_args(self):
        self.assertEqual(Position(1, -1).norm, m.sqrt(2))
        self.assertEqual(Position(-1, 1).norm, m.sqrt(2))
        self.assertEqual(Position(-1, -1).norm, m.sqrt(2))

    def test_norm_with_others_args(self):
        self.assertEqual(Position(3, 4).norm, 5)

    def test_rotate_with_unity_1(self):
        pos = Position(1, 0)
        test_angle = np.pi/2
        self.assertEqual(rotate(pos, test_angle), Position(0, 1))

    def test_rotate_with_unity_2(self):
        pos = Position(0, 1)
        test_angle = np.pi/2
        self.assertEqual(rotate(pos, test_angle), Position(-1, 0))

    def test_rotate_with_unity_3(self):
        pos = Position(-1, 0)
        test_angle = np.pi / 2
        self.assertEqual(rotate(pos, test_angle), Position(0, -1))

    def test_rotate_with_unity_4(self):
        pos = Position(0, -1)
        test_angle = np.pi / 2
        self.assertEqual(rotate(pos, test_angle), Position(1, 0))

    def test_rotate_with_real_args(self):
        pos = Position(526, 878)
        test_angle = 2.14675
        self.assertEqual(rotate(pos, test_angle), Position(-1022.833, -37.052))

    def test_rotate_return_type(self):
        pos = Position(526, 878)
        test_angle = 1.234
        res = rotate(pos, test_angle)
        self.assertTrue(type(res) is Position)

    def test_rotate_identity(self):
        pos = Position(526, 878)
        test_angle = 1.234
        res = rotate(pos, test_angle)
        self.assertTrue(pos is not res)

    def test_normalized_with_unity_pos(self):
        pos = Position(1, 0)
        self.assertEqual(normalized(pos), Position(1, 0))

    def test_normalized_with_unity_neg(self):
        pos = Position(0, -1)
        self.assertEqual(normalized(pos), Position(0, -1))

    def test_normalized_with_args(self):
        pos = Position(10, 10)
        self.assertEqual(normalized(pos), Position(m.sqrt(2) / 2, m.sqrt(2) / 2))

    def test_normalized_return_type(self):
        pos = Position(526, 878)
        res = normalized(pos)
        self.assertTrue(type(res) is Position)

    def test_normalized_identity(self):
        pos = Position(526, 878)
        res = normalized(pos)
        self.assertTrue(pos is not res)

    def test_perpendicular_with_unity(self):
        pos = Position(1, 0)
        self.assertEqual(perpendicular(pos), Position(0, 1))

    def test_perpendicular_with_args(self):
        pos = Position(2, 2)
        self.assertEqual(perpendicular(pos), Position(-np.sqrt(2)/2, np.sqrt(2)/2))

    def test_perpendicular_identity(self):
        pos = Position(2, 2)
        res = perpendicular(pos)
        self.assertTrue(pos is not res)


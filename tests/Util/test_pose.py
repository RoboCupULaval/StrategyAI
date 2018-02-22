
import unittest
import numpy as np
from Util import Position, Pose
from Util.pose import wrap_to_pi, wrap_to_2pi, compare_angle


class TestPose(unittest.TestCase):

    def test_init_without_arg(self):
        pass

    def test_init_no_orientation(self):
        pass

    def test_init_with_args(self):
        pass

    def test_get_position(self):
        pass

    def test_set_position(self):
        pass

    def test_get_orientation(self):
        pass

    def test_set_orientation(self):
        pass

    def test_get_x(self):
        pass

    def test_set_x(self):
        pass

    def test_get_y(self):
        pass

    def test_set_y(self):
        pass

    def test_add_with(self):
        pass

    def test_sub_with(self):
        pass

    def test_equal_with(self):
        pass

    def test_not_equal(self):
        pass

    def test_from_values(self):
        pass

    def test_from_dict(self):
        pass

    def test_to_dict(self):
        pass

    def test_wrap_to_pi_with_zero(self):
        self.assertEqual(wrap_to_pi(0), 0)

    def test_wrap_to_pi_with_edge_case_pos(self):
        self.assertEqual(wrap_to_pi(np.pi), -np.pi)

    def test_wrap_to_pi_with_edge_case_neg(self):
        self.assertEqual(wrap_to_pi(-np.pi), -np.pi)

    def test_wrap_to_pi_with_edge_case_zero(self):
        self.assertEqual(wrap_to_pi(2 * np.pi), 0)

    def test_wrap_to_2pi(self):
        pass

    def test_compare_angle(self):
        pass

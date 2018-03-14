
import unittest
from math import pi

from Util import Position, Pose

__author__ = 'Simon Bouchard'

A_X = 123.4
A_Y = -456.7
A_ORIENTATION = 1.234

A_POS = Position(A_X, A_Y)
A_DIFFERENT_POS = A_POS + Position(314, -15)

A_POSE = Pose(A_POS, A_ORIENTATION)
A_SAME_POSE = Pose(A_POS, A_ORIENTATION)
A_DIFFERENT_POSE = Pose(A_DIFFERENT_POS, A_ORIENTATION+0.123)
A_POSE_WITH_DIFFERENT_POS = Pose(A_DIFFERENT_POS, A_ORIENTATION)
A_POSE_WITH_DIFFERENT_ORIENTATION = Pose(A_POS, A_ORIENTATION-0.987)

A_DICT = {'x': A_X, 'y': A_Y, 'orientation': A_ORIENTATION}
A_WRONG_DICT = {'x': A_X, 'y': A_Y, 'theta': 0}


AN_ANGLE_LESS_THAN_PI = 1.234
AN_ANGLE_GREATER_THAN_PI = pi + 1


class TestPose(unittest.TestCase):

    def test_zero_pose_orientation(self):
        pose = Pose()
        self.assertEqual(pose.position, Position())
        self.assertEqual(pose.orientation, 0)

    def test_pose_orientation_args(self):
        pose = Pose(A_POS, A_ORIENTATION)
        self.assertEqual(pose.position, A_POS)
        self.assertEqual(pose.orientation, A_ORIENTATION)

    def test_new_with_position(self):
        pose = Pose(A_POS)
        self.assertEqual(pose.position, A_POS)
        self.assertEqual(pose.orientation, 0)

    def test_new_with_pos_position_copy(self):
        pose = Pose(A_POS)
        self.assertIsNot(pose.position, A_POS)

    def test_x_y_orientation_args(self):
        pose = Pose.from_values(A_X, A_Y, A_ORIENTATION)
        self.assertEqual(pose.x, A_X)
        self.assertEqual(pose.y, A_Y)
        self.assertEqual(pose.orientation, A_ORIENTATION)

    def test_pose_from_dict(self):
        pose = Pose.from_dict(A_DICT)
        self.assertEqual(pose.x, A_DICT['x'])
        self.assertEqual(pose.y, A_DICT['y'])
        self.assertEqual(pose.orientation, A_DICT['orientation'])

    def test_wrong_dict(self):
        with self.assertRaises(KeyError):
            Pose.from_dict(A_WRONG_DICT)

    def test_extract_dict(self):
        pose_dict = A_POSE.to_dict()
        self.assertDictEqual(pose_dict, A_DICT)

    def test_copy_position_from_pose(self):
        A_POSE.position = A_POS
        self.assertIsNot(A_POSE.position, A_POS)

    def test_add_pose_and_position(self):
        self.assertEqual(A_POSE + A_DIFFERENT_POS, Pose(A_POSE.position + A_DIFFERENT_POS, A_POSE.orientation))

    def test_pose_plus_position_to_pose(self):
        added_pose = A_POSE + A_DIFFERENT_POS
        self.assertIsNot(added_pose, A_POSE)

    def test_equality(self):
        self.assertEqual(A_POSE, A_SAME_POSE)

    def test_unequality_orientation(self):
        self.assertNotEqual(A_POSE, A_POSE_WITH_DIFFERENT_ORIENTATION)

    def test_unequality_with_position(self):
        self.assertNotEqual(A_POSE, A_POSE_WITH_DIFFERENT_POS)

    def test_unequality(self):
        self.assertNotEqual(A_POSE, A_DIFFERENT_POSE)

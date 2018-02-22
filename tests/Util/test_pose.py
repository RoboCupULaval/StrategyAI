
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

    def test_givenNoArg_whenNew_thenZeroPose(self):
        pose = Pose()
        self.assertEqual(pose.position, Position())
        self.assertEqual(pose.orientation, 0)

    def test_givenPositionAndOrientation_whenNew_thenReturnNewPose(self):
        pose = Pose(A_POS, A_ORIENTATION)
        self.assertEqual(pose.position, A_POS)
        self.assertEqual(pose.orientation, A_ORIENTATION)

    def test_givenPosition_whenNew_thenReturnNewPose(self):
        pose = Pose(A_POS)
        self.assertEqual(pose.position, A_POS)
        self.assertEqual(pose.orientation, 0)

    def test_givenPosition_whenNew_thenReturnPoseWithPositionCopy(self):
        pose = Pose(A_POS)
        self.assertIsNot(pose.position, A_POS)

    def test_givenXYOrientation_whenFromValues_thenReturnNewPose(self):
        pose = Pose.from_values(A_X, A_Y, A_ORIENTATION)
        self.assertEqual(pose.x, A_X)
        self.assertEqual(pose.y, A_Y)
        self.assertEqual(pose.orientation, A_ORIENTATION)

    def test_givenDict_whenFromDict_thenReturnNewPose(self):
        pose = Pose.from_dict(A_DICT)
        self.assertEqual(pose.x, A_DICT['x'])
        self.assertEqual(pose.y, A_DICT['y'])
        self.assertEqual(pose.orientation, A_DICT['orientation'])

    def test_givenWrongDict_whenFromDict_thenThrowsKeyError(self):
        with self.assertRaises(KeyError):
            Pose.from_dict(A_WRONG_DICT)

    def test_givenPose_whenToDict_thenReturnDict(self):
        pose_dict = A_POSE.to_dict()
        self.assertDictEqual(pose_dict, A_DICT)

    def test_givenPose_whenSettingPosition_thenSetPositionCopy(self):
        A_POSE.position = A_POS
        self.assertIsNot(A_POSE.position, A_POS)

    def test_givenPoseAndPosition_whenAddingPosition_thenReturnAddition(self):
        self.assertEqual(A_POSE + A_DIFFERENT_POS, Pose(A_POSE.position + A_DIFFERENT_POS, A_POSE.orientation))

    def test_givenPoseAndPosition_whenAddingPosition_thenReturnDifferentPose(self):
        added_pose = A_POSE + A_DIFFERENT_POS
        self.assertIsNot(added_pose, A_POSE)

    def test_givenPoseAndSamePose_whenTestEquality_thenTrue(self):
        self.assertEqual(A_POSE, A_SAME_POSE)

    def test_givenPoseAndDifferentOrientationPose_whenTestEquality_thenFalse(self):
        self.assertNotEqual(A_POSE, A_POSE_WITH_DIFFERENT_ORIENTATION)

    def test_givenPoseAndDifferentPositionPose_whenTestEquality_thenFalse(self):
        self.assertNotEqual(A_POSE, A_POSE_WITH_DIFFERENT_POS)

    def test_givenPoseAndDifferentPose_whenTestEquality_thenFalse(self):
        self.assertNotEqual(A_POSE, A_DIFFERENT_POSE)


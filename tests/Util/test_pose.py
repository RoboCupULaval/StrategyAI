
import unittest
from math import pi

from Util import Position, Pose
from Util.pose import wrap_to_pi, compare_angle

A_X = 123.4
A_Y = -456.7
A_ORIENTATION = 1.234

A_POS = Position(A_X, A_Y)
A_DIFFERENT_POS = A_POS + Position(314, -15)

A_POSE = Pose(A_POS, A_ORIENTATION)
A_DIFFERENT_POSE = Pose(A_DIFFERENT_POS, A_ORIENTATION+0.123)
A_POSE_WITH_DIFFERENT_POS = Pose(A_DIFFERENT_POS, A_ORIENTATION)
A_POSE_WITH_DIFFERENT_ORIENTATION = Pose(A_POS, A_ORIENTATION-0.987)

A_DICT = {'x': A_X, 'y': A_Y, 'orientation': A_ORIENTATION}


class TestPose(unittest.TestCase):

    def test_givenNoArg_whenNew_thenZeroPose(self):
        pass

    def test_givenPositionAndOrientation_whenNew_thenReturnNewPose(self):
        pass

    def test_givenPosition_whenNew_thenReturnNewPose(self):
        pass

    def test_givenPosition_whenNew_thenReturnPoseWithPositionCopy(self):
        pass

    def test_givenXYOrientation_whenFromValues_thenReturnNewPose(self):
        pass

    def test_givenDict_whenFromDict_thenReturnNewPose(self):
        pass

    def test_givenWrongDict_whenFromDict_thenThrowsKeyError(self):
        pass

    def test_givenPose_whenToDict_thenReturnDict(self):
        pass

    def test_givenPose_whenSettingPosition_thenSetPositionCopy(self):
        pass

    def test_givenPoseAndPosition_whenAddingPosition_thenReturnAddition(self):
        pass

    def test_givenPoseAndPosition_whenAddingPosition_thenReturnDifferentPose(self):
        pass

    def test_givenPoseAndSamePose_whenTestEquality_thenTrue(self):
        pass

    def test_givenPoseAndDifferentPose_whenTestEquality_thenFalse(self):
        pass

    # TODO: vvvv eventually move to geometry unit_test vvvv

    def test_givenOrientation_whenWrapToPi_thenReturnWrappedOrientation(self):
        pass

    def test_givenAngleAndSameAngle_whenCompareAngle_thenTrue(self):
        pass

    def test_givenAngleAndSameAnglePlus2Pi_whenCompareAngle_thenTrue(self):
        pass

    def test_givenAngleAndDifferentAngle_whenCompareAngle_thenFalse(self):
        pass

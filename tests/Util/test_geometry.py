# Under MIT License, see LICENSE.txt

import unittest

import numpy as np
import math as m

from Util import Position
from Util.geometry import compare_angle, wrap_to_pi, perpendicular, normalize, are_close, rotate
# from Util.geometry import get_closest_point_on_segment, get_closest_point_on_line


__author__ = 'RoboCupULaval'

A_X = 123.4
A_Y = -56.7

A_POS = Position(A_X, A_Y)
A_SAME_POS = Position(A_X, A_Y)
A_DIFFERENT_POS = Position(A_X+123, A_Y-456)
A_ZERO_POS = Position(0, 0)

A_POS_ANGLE = 1.234
A_NEG_ANGLE = -1.234
AN_ANGLE_LESS_THAN_PI = 1.234
AN_ANGLE_GREATER_THAN_PI = m.pi + 1

A_POS_ROTATED_BY_A_POS_ANGLE = Position(94.294, 97.730)
A_POS_ROTATED_BY_A_NEG_ANGLE = Position(-12.735, -135.205)

A_POS_NORM = np.linalg.norm(A_POS.array)
A_POS_NORMALIZED = Position(A_X, A_Y) / A_POS_NORM

A_POS_PERPENDICULAR = Position(-A_Y, A_X) / A_POS_NORM

A_POS_OFFSET_BY_1 = A_POS + Position(1, 0)
A_POS_OFFSET_BY_LESS_THAN_1 = A_POS_OFFSET_BY_1 - Position(0.001, 0)


class TestGeometry(unittest.TestCase):

    def test_get_closest_point_on_line(self):
        pass

    def test_get_closest_point_on_segment(self):
        pass

    def test_givenOrientationLessThanPi_whenWrapToPi_thenReturnWrappedOrientation(self):
        self.assertEqual(wrap_to_pi(AN_ANGLE_LESS_THAN_PI), AN_ANGLE_LESS_THAN_PI)

    def test_givenOrientationGreaterThanPi_whenWrapToPi_thenReturnWrappedOrientation(self):
        self.assertEqual(wrap_to_pi(AN_ANGLE_GREATER_THAN_PI), AN_ANGLE_GREATER_THAN_PI - 2*m.pi)

    def test_givenAngleAndSameAngle_whenCompareAngle_thenTrue(self):
        self.assertTrue(compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI))

    def test_givenAngleAndSameAnglePlus2Pi_whenCompareAngle_thenTrue(self):
        self.assertTrue(compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI + 2*m.pi))

    def test_givenAngleAndDifferentAngle_whenCompareAngle_thenFalse(self):
        self.assertFalse(compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_GREATER_THAN_PI))

    def test_givenDifferentAngleInTolAndTol_whenCompareAngle_thenTrue(self):
        self.assertTrue(compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI+0.99, abs_tol=1))

    def test_givenPositionAndPositiveAngle_whenRotate_thenReturnRotatedPosition(self):
        self.assertEqual(rotate(A_POS, A_POS_ANGLE), A_POS_ROTATED_BY_A_POS_ANGLE)

    def test_givenPositionAndNegativeAngle_whenRotate_thenReturnRotatedPosition(self):
        self.assertEqual(rotate(A_POS, A_NEG_ANGLE), A_POS_ROTATED_BY_A_NEG_ANGLE)

    def test_givenPositionAndAngle_whenRotate_thenReturnIsPosition(self):
        self.assertIsInstance(rotate(A_POS, A_POS_ANGLE), Position)

    def test_givenPositionAndAngle_whenRotate_thenReturnIsNotSame(self):
        self.assertIsNot(rotate(A_POS, A_POS_ANGLE), A_POS)

    def test_givenPosition_whenNormalized_thenReturnNormalizedPosition(self):
        self.assertEqual(normalize(A_POS), A_POS_NORMALIZED)

    def test_givenZeroPosition_whenNormalized_thenThrowsZeroDivisionError(self):
        with self.assertRaises(ZeroDivisionError):
            print(normalize(A_ZERO_POS))

    def test_givenPosition_whenNormalized_thenReturnIsPosition(self):
        self.assertIsInstance(normalize(A_POS), Position)

    def test_givenPosition_whenNormalized_thenReturnIsNotSame(self):
        self.assertIsNot(normalize(A_POS), A_POS)

    def test_givenPosition_whenPerpendicular_thenReturnPerpendicularPosition(self):
        self.assertEqual(perpendicular(A_POS), A_POS_PERPENDICULAR)

    def test_givenPosition_whenPerpendicular_thenReturnIsNotSame(self):
        self.assertIsNot(perpendicular(A_POS), A_POS)

    def test_givenPosition_whenPerpendicular_thenReturnIsPosition(self):
        self.assertIsInstance(perpendicular(A_POS), Position)

    def test_givenSamePositions_whenIsClose_thenReturnTrue(self):
        self.assertTrue(are_close(A_POS, A_SAME_POS))

    def test_givenDifferentPositions_whenIsClose_thenReturnFalse(self):
        self.assertFalse(are_close(A_POS, A_DIFFERENT_POS))

    def test_givenPositionOffsetByTolerance_whenIsClose_thenReturnFalse(self):
        self.assertFalse(are_close(A_POS, A_POS_OFFSET_BY_1, abs_tol=1))

    def test_givenPositionOffsetByLessThanTolerance_whenIsClose_thenReturnTrue(self):
        self.assertTrue(are_close(A_POS, A_POS_OFFSET_BY_LESS_THAN_1, abs_tol=1))

if __name__ == '__main__':
    unittest.main()

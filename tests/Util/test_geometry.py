# Under MIT License, see LICENSE.txt


import unittest

import numpy as np
import math as m

from Util import Position
from Util.geometry import get_line_equation, get_nearest, get_closest_point_on_line, compare_angle, wrap_to_pi,\
    perpendicular, normalized, is_close, rotate

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

A_POS_NORM = np.linalg.norm(A_POS)
A_POS_NORMALIZED = Position(A_X, A_Y) / A_POS_NORM

A_POS_PERPENDICULAR = Position(-A_Y, A_X) / A_POS_NORM

A_POS_OFFSET_BY_1 = A_POS + Position(1, 0)
A_POS_OFFSET_BY_LESS_THAN_1 = A_POS_OFFSET_BY_1 - Position(0.001, 0)


class TestGeometry(unittest.TestCase):

    def setUp(self):
        self.position = Position()
        self.positionN = Position(0, 10000)
        self.positionNE = Position(10000, 10000)
        self.positionNO = Position(-10000, 10000)
        self.positionS = Position(0, -10000)
        self.positionSE = Position(10000, -10000)
        self.positionSO = Position(-10000, -10000)

    def test_get_distance(self):
        dist = (self.position - self.positionN).norm
        self.assertEqual(dist, 10000)

        approx_dist = (self.positionNE - self.positionSO).norm
        compValue = m.sqrt(2*(20000**2))
        self.assertAlmostEqual(approx_dist, compValue) # On veut quelle précision pour geo?

    def test_get_angle(self):
        self.assertEqual((self.positionN - self.position).angle, m.pi/2)
        self.assertEqual((self.positionNE - self.position).angle, m.pi/4)
        self.assertEqual((self.positionNO - self.position).angle, 3*m.pi/4)
        self.assertEqual((self.positionSE - self.position).angle, -1*m.pi/4)
        self.assertEqual((self.positionSO - self.position).angle, -3*m.pi/4)

    def test_get_nearest(self):
        list_of_positions = [self.positionNE, self.positionSE, self.positionSO, self.positionN]
        nearest = get_nearest(self.position, list_of_positions)
        self.assertEqual(nearest[0], self.positionN)

        list_of_positions.remove(self.positionN)
        list_of_positions.append(self.positionS)
        nearest = get_nearest(self.position, list_of_positions)
        self.assertEqual(nearest[0], self.positionS)

    def test_get_line_equation(self):
        self.assertEqual(get_line_equation(self.positionNE, self.positionSO), (1, 0))
        self.assertEqual(get_line_equation(self.positionNE, self.positionNO), (0, 10000))

    def test_get_closest_point_on_line(self):
        # Quand le point est nul (0, 0)
        close_null_point = get_closest_point_on_line(self.positionNE, self.positionSE, self.positionNO)
        self.assertEqual(close_null_point, self.position)
        # Quand le point est sur une position à l'extérieure des deux points
        close_nonexistent_point = get_closest_point_on_line(self.positionSE, self.position, self.positionN)
        self.assertEqual(close_nonexistent_point, self.positionS)
        # Point normal
        close_point = get_closest_point_on_line(self.positionNE, self.position, self.positionN)
        self.assertEqual(close_point, self.positionN)

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
        self.assertEqual(normalized(A_POS), A_POS_NORMALIZED)

    def test_givenZeroPosition_whenNormalized_thenThrowsZeroDivisionError(self):
        with self.assertRaises(ZeroDivisionError):
            print(normalized(A_ZERO_POS))

    def test_givenPosition_whenNormalized_thenReturnIsPosition(self):
        self.assertIsInstance(normalized(A_POS), Position)

    def test_givenPosition_whenNormalized_thenReturnIsNotSame(self):
        self.assertIsNot(normalized(A_POS), A_POS)

    def test_givenPosition_whenPerpendicular_thenReturnPerpendicularPosition(self):
        self.assertEqual(perpendicular(A_POS), A_POS_PERPENDICULAR)

    def test_givenPosition_whenPerpendicular_thenReturnIsNotSame(self):
        self.assertIsNot(perpendicular(A_POS), A_POS)

    def test_givenPosition_whenPerpendicular_thenReturnIsPosition(self):
        self.assertIsInstance(perpendicular(A_POS), Position)

    def test_givenSamePositions_whenIsClose_thenReturnTrue(self):
        self.assertTrue(is_close(A_POS, A_SAME_POS))

    def test_givenDifferentPositions_whenIsClose_thenReturnFalse(self):
        self.assertFalse(is_close(A_POS, A_DIFFERENT_POS))

    def test_givenPositionOffsetByTolerance_whenIsClose_thenReturnFalse(self):
        self.assertFalse(is_close(A_POS, A_POS_OFFSET_BY_1, abs_tol=1))

    def test_givenPositionOffsetByLessThanTolerance_whenIsClose_thenReturnTrue(self):
        self.assertTrue(is_close(A_POS, A_POS_OFFSET_BY_LESS_THAN_1, abs_tol=1))

if __name__ == '__main__':
    unittest.main()
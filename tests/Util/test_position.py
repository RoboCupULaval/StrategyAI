import math as m
import unittest

import numpy as np

from Util import Position
from Util.position import normalized, perpendicular, rotate, is_close


A_POS_ANGLE = 1.234
A_NEG_ANGLE = -1.234
A_ZERO_ANGLE = 0
A_90_ANGLE = np.pi/2
A_180_ANGLE = np.pi

A_X = 123.4
A_Y = -56.7

A_LIST = [A_X, A_Y]
A_ARRAY = np.array(A_LIST)
A_DICT = {'x': A_X, 'y': A_Y}

A_ZERO_POS = Position(0, 0)
A_POS = Position(A_X, A_Y)
A_SAME_POS = Position(A_X, A_Y)
A_DIFFERENT_POS = Position(A_X+123, A_Y-456)

# TODO: vvvv eventually move to geometry unit_test vvvv

A_POS_ROTATED_BY_A_POS_ANGLE = Position(94.294, 97.730)
A_POS_ROTATED_BY_A_NEG_ANGLE = Position(-12.735, -135.205)

A_POS_NORM = np.linalg.norm(A_POS)
A_POS_NORMALIZED = Position(A_X, A_Y) / A_POS_NORM

A_POS_PERPENDICULAR = Position(-A_Y, A_X) / A_POS_NORM

A_POS_OFFSET_BY_1 = A_POS + Position(1, 0)
A_POS_OFFSET_BY_LESS_THAN_1 = A_POS_OFFSET_BY_1 - Position(0.001, 0)


class TestPosition(unittest.TestCase):

    def test_givenNoArgs_whenNew_thenZeroPosition(self):
        self.assertEqual(Position(), A_ZERO_POS)

    def test_givenArgs_whenNew_thenPositionIsInstantiated(self):
        pos = Position(A_X, A_Y)
        self.assertEqual(pos.x, A_X)
        self.assertEqual(pos.y, A_Y)

    def test_givenNumpyArray_whenFromArray_thenPositionIsInstantiated(self):
        pos = Position.from_array(A_ARRAY)
        self.assertEqual(pos.x, A_ARRAY[0])
        self.assertEqual(pos.y, A_ARRAY[1])

    def test_givenNumpyArray_whenFromArray_thenPositionIsCopy(self):
        pos = Position.from_array(A_ARRAY)
        self.assertIsNot(pos, A_ARRAY)

    def test_givenList_whenFromList_thenPositionIsInstantiated(self):
        pos = Position.from_list(A_LIST)
        self.assertEqual(pos.x, A_LIST[0])
        self.assertEqual(pos.y, A_LIST[1])

    def test_givenDict_whenFromDict_thenPositionIsInstantiated(self):
        pos = Position.from_dict(A_DICT)
        self.assertEqual(pos.x, A_DICT['x'])
        self.assertEqual(pos.y, A_DICT['y'])

    def test_givenSamePosition_whenTestEquality_thenTrue(self):
        self.assertTrue(A_POS == A_SAME_POS)

    def test_givenDifferentPosition_whenTestEquality_thenFalse(self):
        self.assertFalse(A_POS == A_DIFFERENT_POS)

    def test_givenSamePosition_whenTestInequality_thenFalse(self):
        self.assertFalse(A_POS != A_SAME_POS)

    def test_givenDifferentPosition_whenTestInequality_thenTrue(self):
        self.assertTrue(A_POS != A_DIFFERENT_POS)

    def test_givenPosition_whenGetAngle_thenAngle(self):
        pos_angle = m.atan2(A_POS.y, A_POS.x)
        self.assertEqual(A_POS.angle, pos_angle)

    def test_givenZeroPosition_whenGetAngle_thenZero(self):
        self.assertEqual(A_ZERO_POS.angle, A_ZERO_ANGLE)

    def test_givenPosition_whenGetNorm_thenNorm(self):
        self.assertEqual(A_POS.norm, A_POS_NORM)

    # TODO: vvvv eventually move to geometry unit_test vvvv

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

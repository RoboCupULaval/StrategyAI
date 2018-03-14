# Under MIT License, see LICENSE.txt

import math

import pytest

import numpy as np

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
AN_ANGLE_GREATER_THAN_PI = math.pi + 1

A_POS_ROTATED_BY_A_POS_ANGLE = Position(94.294, 97.730)
A_POS_ROTATED_BY_A_NEG_ANGLE = Position(-12.735, -135.205)

A_POS_NORM = np.linalg.norm(A_POS.array)
A_POS_NORMALIZED = Position(A_X, A_Y) / A_POS_NORM

A_POS_PERPENDICULAR = Position(-A_Y, A_X) / A_POS_NORM

A_POS_OFFSET_BY_1 = A_POS + Position(1, 0)
A_POS_OFFSET_BY_LESS_THAN_1 = A_POS_OFFSET_BY_1 - Position(0.001, 0)


def test_wrap_less_than_pi():
    assert wrap_to_pi(AN_ANGLE_LESS_THAN_PI) == AN_ANGLE_LESS_THAN_PI


def test_wrap_more_than_pi():
    assert wrap_to_pi(AN_ANGLE_GREATER_THAN_PI) == AN_ANGLE_GREATER_THAN_PI - 2*math.pi


def test_angle_compare_equality():
    assert compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI)


def test_compare_wraparound():
    assert compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI + 2*math.pi)


def test_angle_unequality_tol():
    assert not compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_GREATER_THAN_PI)


def test_angle_equality_tol():
    assert compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI+0.99, abs_tol=1)


def test_rotation_positive():
    assert rotate(A_POS, A_POS_ANGLE) == A_POS_ROTATED_BY_A_POS_ANGLE


def test_rotation_negative():
    assert rotate(A_POS, A_NEG_ANGLE) == A_POS_ROTATED_BY_A_NEG_ANGLE


def test_rotation_return_position():
    assert isinstance(rotate(A_POS, A_POS_ANGLE), Position)

def test_different_output_rotation():
    assert rotate(A_POS, A_POS_ANGLE) is not A_POS


def test_normalized_position():
    assert normalize(A_POS) == A_POS_NORMALIZED


def test_zero_position_normalize():
    with pytest.raises(ZeroDivisionError):
        normalize(A_ZERO_POS)


def test_normalized_position_type():
    assert isinstance(normalize(A_POS), Position)


def test_different_normalized():
    assert normalize(A_POS) is not A_POS


def test_perpendicular_value():
    assert perpendicular(A_POS) == A_POS_PERPENDICULAR


def test_perpendicular_different():
    assert perpendicular(A_POS) is not A_POS


def test_perpendicular_type():
    assert isinstance(perpendicular(A_POS), Position)


def test_is_close_same_position():
    assert are_close(A_POS, A_SAME_POS)

def test_different_pos_not_close():
    assert not are_close(A_POS, A_DIFFERENT_POS)

def test_unequal_outside_tolerance():
    assert not are_close(A_POS, A_POS_OFFSET_BY_1, abs_tol=1)

def test_equal_inside_tolerance():
    assert are_close(A_POS, A_POS_OFFSET_BY_LESS_THAN_1, abs_tol=1)

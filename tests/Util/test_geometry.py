# Under MIT License, see LICENSE.txt

import numpy as np
import math as m

import pytest

from Util import Position
from Util.geometry import closest_point_on_line
from Util.geometry import compare_angle, wrap_to_pi, perpendicular, normalize, are_close, rotate


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


def test_closest_point_on_line_vertical():
    reference = Position(50, 50)
    start = Position(10, 0)
    end = Position(100, 0)
    assert closest_point_on_line(reference, start=start, end=end) == Position(50, 0)

def test_closest_point_on_line_horizontal():
    reference = Position(50, 50)
    start = Position(0, 10)
    end = Position(0, 100)
    assert closest_point_on_line(reference, start=start, end=end) == Position(0, 50)

def test_closest_point_on_line_diagonal():
    reference = Position(50, 50)
    start = Position(0, 0)
    end = Position(100, 100)
    assert closest_point_on_line(reference, start=start, end=end) == Position(50, 50)

def test_closest_point_on_line_at_zero():
    reference = Position(0, 50)
    start = Position(-100, 0)
    end = Position(100, 0)
    assert closest_point_on_line(reference, start=start, end=end) == Position(0, 0)

def test_closest_point_on_line_outside_range():
    reference = Position(-50, 50)
    start = Position(10, 0)
    end = Position(100, 0)
    assert closest_point_on_line(reference, start=start, end=end) == Position(-50, 0)


def test_wrap_to_pi_with_angle_less_than_pi():
    assert wrap_to_pi(AN_ANGLE_LESS_THAN_PI) == AN_ANGLE_LESS_THAN_PI

def test_wrap_to_pi_with_angle_greater_than_pi():
    assert wrap_to_pi(AN_ANGLE_GREATER_THAN_PI) == AN_ANGLE_GREATER_THAN_PI - 2*m.pi


def test_compare_angle_with_same_angle():
    assert compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI)

def test_compare_angle_with_same_angle_offset_by_2pi():
    assert compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI + 2*m.pi)

def test_compare_angle_with_different_angle():
    assert not compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_GREATER_THAN_PI)

def test_compare_angle_with_tolerance():
    assert compare_angle(AN_ANGLE_LESS_THAN_PI, AN_ANGLE_LESS_THAN_PI+0.99, abs_tol=1)


def test_rotate_by_positive_angle():
    assert rotate(A_POS, A_POS_ANGLE) == A_POS_ROTATED_BY_A_POS_ANGLE

def test_rotate_by_negative_angle():
    assert rotate(A_POS, A_NEG_ANGLE) == A_POS_ROTATED_BY_A_NEG_ANGLE

def test_rotate_return_type():
    assert isinstance(rotate(A_POS, A_POS_ANGLE), Position)

def test_rotate_identity():
    assert rotate(A_POS, A_POS_ANGLE) is not A_POS


def test_normalize_base_case():
    assert normalize(A_POS) == A_POS_NORMALIZED

def test_normalize_with_zero_posisiton():
    with pytest.raises(ZeroDivisionError):
        normalize(A_ZERO_POS)

def test_normalize_return_type():
    assert isinstance(normalize(A_POS), Position)

def test_normalize_identity():
    assert normalize(A_POS) is not A_POS


def test_perpendicular_base_case():
    assert perpendicular(A_POS) == A_POS_PERPENDICULAR

def test_perpendicular_return_type():
    assert isinstance(perpendicular(A_POS), Position)

def test_perpendicular_identity():
    assert perpendicular(A_POS) is not A_POS


def test_are_close_same_positions():
    assert are_close(A_POS, A_SAME_POS)

def test_are_close_different_positions():
    assert not are_close(A_POS, A_DIFFERENT_POS)

def test_are_close_tolerance_limit():
    assert not are_close(A_POS, A_POS_OFFSET_BY_1, abs_tol=1)

def test_are_close_tolerance():
    assert are_close(A_POS, A_POS_OFFSET_BY_LESS_THAN_1, abs_tol=1)

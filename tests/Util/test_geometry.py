# Under MIT License, see LICENSE.txt

import numpy as np
import math as m

import pytest

from Util import Position
from Util.geometry import closest_point_on_line, closest_point_on_segment, closest_point_to_points, \
    intersection_between_lines, find_bisector_of_triangle, angle_between_three_points, Area, \
    intersection_between_segments
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

def test_closest_point_on_line_diagonal_under():
    reference = Position(0, 100)
    start = Position(0, 0)
    end = Position(100, 100)
    assert closest_point_on_line(reference, start=start, end=end) == Position(50, 50)

def test_closest_point_on_line_diagonal_reverse():
    reference = Position(50, 50)
    end = Position(0, 0)
    start = Position(100, 100)
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


def test_closest_point_on_segment():
    reference = Position(50, 50)
    start = Position(10, 0)
    end = Position(100, 0)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(50, 0)

def test_closest_point_on_segment_under():
    reference = Position(0, 100)
    start = Position(10, 10)
    end = Position(100, 100)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(50, 50)

def test_closest_point_on_segment_outside_positive():
    reference = Position(110, 0)
    start = Position(10, 0)
    end = Position(100, 0)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(100, 0)

def test_closest_point_on_segment_outside_negative():
    reference = Position(-10, 0)
    start = Position(10, 0)
    end = Position(100, 0)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(10, 0)

def test_closest_point_on_segment_outside_diagonal():
    reference = Position(91, 110)
    start = Position(10, 10)
    end = Position(100, 100)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(100, 100)

def test_closest_point_on_segment_outside_diagonal_reverse():
    reference = Position(91, 110)
    end = Position(10, 10)
    start = Position(100, 100)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(100, 100)

def test_closest_point_on_segment_outside_diagonal2():
    reference = Position(9, 10)
    start = Position(10, 10)
    end = Position(100, 100)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(10, 10)

def test_closest_point_on_segment_outside_diagonal2_reverse():
    reference = Position(9, 10)
    end = Position(10, 10)
    start = Position(100, 100)
    assert closest_point_on_segment(reference, start=start, end=end) == Position(10, 10)


def test_closest_point_to_points():
    point = Position(0,0)
    points = [Position(0,1), Position(1,1), Position(-2,-1), Position(2,1)]
    assert closest_point_to_points(point, points=points) is points[0]



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


A_LINE = [Position(-1, 0), Position(1, 0)]
A_LINE_PERP = [Position(0, -1), Position(0, 1)]
def test_intersection_lines_perpendicular():
    assert Position(0, 0) == intersection_between_lines(A_LINE[0],
                                                        A_LINE[1],
                                                        A_LINE_PERP[0],
                                                        A_LINE_PERP[1])
A_PERP_POINT_TO_BISECTION = Position(0, 1)
def test_bisector_of_squared_triangle():
    assert Position(0, 0) == find_bisector_of_triangle(A_PERP_POINT_TO_BISECTION,
                                                       A_LINE[0],
                                                       A_LINE[1])


def test_bisector_angle_between_the_intersection_is_the_same():
    A_RANDOM_POINT = Position(np.random.randn(1, 1), 1)
    inter = find_bisector_of_triangle(A_RANDOM_POINT, A_LINE[0], A_LINE[1])
    angle1 = angle_between_three_points(A_LINE[0], A_RANDOM_POINT, inter)
    angle2 = angle_between_three_points(inter, A_RANDOM_POINT, A_LINE[1])
    assert compare_angle(angle1, angle2, abs_tol=0.01)


def test_area_contain_point():
    assert Position(100, 300) in Area(Position(0, 500), Position(500, 0))


ANOTHER_LINE = [Position(0, 2), Position(0, 4)]
def test_intersection_segment_when_a_line_does_not_touch_another_line():
    assert intersection_between_segments(A_LINE[0], A_LINE[1], ANOTHER_LINE[0], ANOTHER_LINE[1]) is None


def test_intersection_segment_when_a_line_intersect_a_perpendicular_line():
    assert Position(0, 0) == intersection_between_segments(A_LINE[0], A_LINE[1], A_LINE_PERP[0], A_LINE_PERP[1])

A_PARA_LINE = [Position(-1, 0), Position(1, 0)]
ANOTHER_PARA_LINE = [Position(-1, 1), Position(1, 1)]
def test_intersection_segment_when_two_paralle_lines():
    assert intersection_between_segments(A_PARA_LINE[0], A_PARA_LINE[1], ANOTHER_PARA_LINE[0], ANOTHER_PARA_LINE[1]) is None

# Under MIT License, see LICENSE.txt

import math as m
import numpy as np

from Util import Position, Pose
from typing import cast

def wrap_to_pi(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def compare_angle(angle1, angle2, abs_tol=0.004) -> bool:
    return m.fabs(wrap_to_pi(angle1 - angle2)) < abs_tol


def rotate(vec: Position, angle) -> Position:
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return Position.from_array(rotation @ vec.array)


def normalize(vec: Position) -> Position:
    if vec.norm == 0:
        raise ZeroDivisionError
    return vec.copy() / vec.norm


def perpendicular(vec: Position) -> Position:
    """Return the orthonormal vector to the np.array([0,0,1]) with right hand rule."""
    return normalize(Position(-vec.y, vec.x))


def are_close(vec1: Position, vec2: Position, abs_tol=0.001) -> bool:
    return (vec1 - vec2).norm < abs_tol


def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)


def closest_point_on_line(reference: Position, start: Position, end: Position) -> Position:
    start_to_end = normalize(end - start)
    start_to_reference = reference - start
    projection = np.inner(start_to_reference.array, start_to_end.array)
    return start + start_to_end * projection


def get_closest_point_on_segment(reference: Position, start: Position, end: Position) -> Position:
    position_on_line = closest_point_on_line(reference, start, end)
    position_on_segment = position_on_line

    # This handle the case where the projection is not between the two points
    outside_x = (reference.array > start.array) or \
                (reference.x < start.x and reference.x < end.x)
    outside_y = (reference.y > start.y and reference.y > end.y) or \
                (reference.y < start.y and reference.y < end.y)
    if outside_x or outside_y:
        if (start - reference).norm < (end - reference).norm:
            position_on_segment = start
        else:
            position_on_segment = end
    return position_on_segment

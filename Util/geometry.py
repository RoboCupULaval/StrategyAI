# Under MIT License, see LICENSE.txt

import math as m
import numpy as np

from Util.pose import Pose
from Util.position import Position
from typing import cast, Sequence, List


def get_angle_between_three_points(start: Position, mid: Position, end: Position) -> float:
    return abs(wrap_to_pi((mid - start).angle - (end - mid).angle))


def wrap_to_pi(angle: float) -> float:
    return (angle + m.pi) % (2 * m.pi) - m.pi


def compare_angle(angle1: float, angle2: float, abs_tol: float=0.004) -> bool:
    return m.fabs(wrap_to_pi(angle1 - angle2)) < abs_tol


def rotate(vec: Position, angle: float) -> Position:
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return Position.from_array(rotation @ vec.array)


def normalize(vec: Position) -> Position:
    if vec.norm == 0:
        raise ZeroDivisionError
    return vec.copy() / vec.norm


def perpendicular(vec: Position) -> Position:
    return normalize(Position(-vec.y, vec.x))


def are_close(vec1: Position, vec2: Position, abs_tol: float=0.001) -> bool:
    return (vec1 - vec2).norm < abs_tol


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min(val, max_val), min_val)


def projection(reference: Position, start: Position, end: Position) -> float:
    start_to_end = normalize(end - start)
    start_to_reference = reference - start
    return np.inner(start_to_reference.array, start_to_end.array).view(float)


def closest_point_on_line(reference: Position, start: Position, end: Position) -> Position:
    return start + normalize(end - start) * projection(reference, start=start, end=end)


def closest_point_on_segment(reference: Position, start: Position, end: Position) -> Position:
    if end == start:
        return start
    proj = projection(reference, start=start, end=end)
    if proj >= (end - start).norm:
        return end
    elif proj <= 0:
        return start
    else:
        return closest_point_on_line(reference, start=start, end=end)


def closest_point_to_points_index(point: Position, points: Sequence[Position]) -> int:
    distances = distance_from_points(point, points=points)
    return np.argmin(distances).view(int)


def closest_point_to_points(point: Position, points: Sequence[Position]) -> Position:
    return points[closest_point_to_points_index(point, points=points)]


def closest_points_from_points(point: Position, points: Sequence[Position]) -> List[Position]:
    distances = distance_from_points(point, points=points)
    sorted_points_distances = sorted(zip(points, distances), key=lambda pair: pair[1])
    return  [p for p, _ in sorted_points_distances]


def distance_from_points(point: Position, points: Sequence[Position]) -> List[float]:
    points_array = np.array([p.array for p in points])
    return cast(List, np.linalg.norm(points_array - point.array).tolist())
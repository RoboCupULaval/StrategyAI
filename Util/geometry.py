# Under MIT License, see LICENSE.txt

import math as m
import numpy as np

from Util.position import Position
from typing import cast, Sequence, List, Union, Optional


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return "Line(p1={}, p2={})".format(self.p1, self.p2)

    @property
    def direction(self):
        return normalize(self.p2 - self.p1)

    @property
    def length(self):
        return (self.p2 - self.p1).norm

class Area:
    def __init__(self, a, b):
        neg_x, pos_x = min(a.x, b.x), max(a.x, b.x)
        neg_y, pos_y = min(a.y, b.y), max(a.y, b.y)
        self.upper_left = Position(neg_x, pos_y)
        self.upper_right = Position(pos_x, pos_y)
        self.lower_right = Position(pos_x, neg_y)
        self.lower_left = Position(neg_x, neg_y)

    def point_inside(self, p: Position) -> bool:
        return self.left <= p.x <= self.right and \
               self.bottom <= p.y <= self.top

    def __str__(self):
        return "Area(top={}, bottom={}, right={}, left={})".format(self.top, self.bottom, self.right, self.left)

    def __contains__(self, item: Union["Pose", Position]):
        if item.__class__.__name__ == "Pose":  # Prevent importing Pose
            return self.point_inside(item.position)
        elif isinstance(item, Position):
            return self.point_inside(item)
        else:
            raise ValueError("You can only test if a position or a pose is contained inside the area.")

    def intersect(self, seg: Line):
        assert isinstance(seg, Line)
        if self.point_inside(seg.p1) and self.point_inside(seg.p2):
            return []

        inters = []
        for segment in self.segments:
            inter = intersection_between_segments(segment.p1, segment.p2, seg.p1, seg.p2)
            if inter is not None:
                inters.append(inter)
        return inters


    def intersect_with_line(self, line: Line):
        assert isinstance(line, Line)

        inters = []
        for segment in self.segments:
            inter = intersection_between_line_and_segment(segment.p1, segment.p2, line.p1, line.p2)
            if inter is not None:
                inters.append(inter)
        return inters

    def closest_border_point(self, p: Position):
        closest = None
        for segment in self.segments:
            dist = closest_point_on_segment(p, segment.p1, segment.p2)
            if closest is None or (dist - p).norm < (closest - p).norm:
                closest = dist
        return closest

    @property
    def segments(self):
        return [Line(self.upper_left,  self.upper_right),
                Line(self.upper_right, self.lower_right),
                Line(self.lower_right, self.lower_left),
                Line(self.lower_left,  self.upper_left)]

    @property
    def center(self):
        return self.lower_left + Position(self.width / 2, self.height / 2)

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def top(self):
        return self.upper_left.y

    @property
    def bottom(self):
        return self.lower_right.y

    @property
    def left(self):
        return self.upper_left.x

    @property
    def right(self):
        return self.lower_right.x

    @classmethod
    def pad(cls, area, padding=0):
        return Area.from_limits(area.top + padding, area.bottom - padding,
                                area.right + padding, area.left - padding)

    @classmethod
    def from_limits(cls, top, bottom, right, left):
        return cls(Position(left, top), Position(right, bottom))





def find_bisector_of_triangle(c, a, b):
    """
    Where 'c' is the origin of the bisector and the intersection of the bissectrice 'i' is on the segment 'ab'.
    The angle bae and aci is the same as icb
    """
    ab, cb, ca = a-b, c-b, c-a
    ia = ab * ca.norm / (ca.norm + cb.norm)
    return a - ia


def intersection_between_segments(a1, a2, b1, b2) -> Optional[Position]:
    try:
        inter = intersection_between_lines(a1, a2, b1, b2)
    except ValueError:
        return None

    if inter == closest_point_on_segment(inter, a1, a2) == closest_point_on_segment(inter, b1, b2):
        return inter
    return None


def intersection_between_line_and_segment(s1, s2, l1, l2) -> Optional[Position]:
    try:
        inter = intersection_between_lines(s1, s2, l1, l2)
    except ValueError:
        return None

    if inter == closest_point_on_segment(inter, s1, s2):
        return inter
    return None

def intersection_between_lines(a1, a2, b1, b2) -> Position:
    s = np.vstack([a1.array, a2.array, b1.array, b2.array])
    h = np.hstack((s, np.ones((4, 1))))
    l1 = np.cross(h[0], h[1])  # first line
    l2 = np.cross(h[2], h[3])  # second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:
        raise ValueError("Parallel lines")
    return Position(x / z, y / z)


def intersection_line_and_circle(cp: Position, cr: float, lp1: Position, lp2: Position) -> List[Position]:
    # Based on http://mathworld.wolfram.com/Circle-LineIntersection.html
    lp1 = lp1.copy() - cp
    lp2 = lp2.copy() - cp
    d = lp2 - lp1
    det = lp1.x * lp2.y - lp2.x * lp1.y

    delta = cr**2 * d.norm**2 - det**2
    if delta < 0:
        return []  # No intersection

    x1 = (det * d.y + np.sign(d.y) * d.x * np.sqrt(delta)) / (d.norm**2)
    y1 = (-det * d.x + abs(d.y) * np.sqrt(delta)) / (d.norm**2)
    if delta == 0:
        return [Position(x1, y1) + cp]  # Tangential

    x2 = (det * d.y - np.sign(d.y) * d.x * np.sqrt(delta)) / (d.norm**2)
    y2 = (-det * d.x - abs(d.y) * np.sqrt(delta)) / (d.norm**2)
    return [Position(x1, y1) + cp, Position(x2, y2) + cp]


def angle_between_three_points(start: Position, mid: Position, end: Position) -> float:
    return abs(wrap_to_pi((mid - start).angle - (mid - end).angle))


def find_signed_delta_angle(target_angle, source_angle) -> float:
    return m.atan2(np.sin(target_angle - source_angle), np.cos(target_angle - source_angle))


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


def random_direction():
    return normalize(Position.from_array(np.random.randn(2)))

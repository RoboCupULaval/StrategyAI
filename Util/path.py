from typing import List

import collections

from numpy.core.multiarray import ndarray

from Util import Position


# pylint: disable=invalid-name
class Path(collections.MutableSequence):  # pylint: disable=too-many-ancestors

    def __init__(self, start=None, target=None):
        self.points = [start, target]

    def filter(self, threshold):
        if len(self) > 2:
            kept_points = [self.start]
            for point in self[1:]:
                if (point - kept_points[-1]).norm >= threshold:
                    kept_points.append(point)

            kept_points.append(self.target)

            if (kept_points[-2] - kept_points[-1]).norm < threshold:
                kept_points.pop(-2)

            self.points = kept_points

    @classmethod
    def from_array(cls, start: ndarray, target: ndarray):
        return Path(Position.from_array(start), Position.from_array(target))

    @classmethod
    def from_points(cls, points_list: List[Position]):
        if len(points_list) < 2:
            raise ValueError('Cannot create a path with less then two points')

        path = cls()
        path.points = points_list
        return path

    @property
    def start(self):
        return self[0]

    @start.setter
    def start(self, v: Position):
        self[0] = v

    @property
    def target(self):
        return self[-1]

    @target.setter
    def target(self, v: Position):
        self[-1] = v

    @property
    def next_position(self):
        return self[1]

    def copy(self):
        return Path.from_points(self.points)

    @property
    def length(self):
        segments = [(point - next_point).norm for point, next_point in zip(self, self[1:])]
        return sum(segments)

    def __iter__(self):
        for p in self.points:
            yield p

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, key, value):
        self.points[key] = value

    def __delitem__(self, key):
        del self.points[key]

    def insert(self, index, value):
        self.points.insert(index, value)

    def __len__(self):
        return len(self.points)

    def __add__(self, other):
        return Path.from_points(self.points + other.points[1:])

    def __repr__(self):
        return 'Path(start={}, target={})'.format(self.start, self.target)

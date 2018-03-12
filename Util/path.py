from typing import List

import collections

from numpy.core.multiarray import ndarray

from Util import Position


class Path(collections.MutableSequence):

    def __init__(self, start=Position(),  end=Position()):
        self.points = [start, end]

    def filter(self, threshold):
        if len(self) > 2:
            new_points = [self.start]
            for p1, p2 in zip(self[1:], self[2:]):
                if (p1 - p2).norm >= threshold:
                    new_points.append(p1)
            new_points.append(self.goal)
            self.points = new_points

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
    def goal(self):
        return self[-1]

    @goal.setter
    def goal(self, v: Position):
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
        return 'Path(start={}, goal={})'.format(self.start, self.goal)

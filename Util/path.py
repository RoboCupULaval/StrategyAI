from typing import Sequence, Union

from collections import MutableSequence

from numpy.core.multiarray import ndarray

from Util import Position


class Path(MutableSequence):

    def __init__(self, start: Position, target: Position):
        self.points = [start, target]

    def filter(self, threshold: Union[int, float]):
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
    def from_array(cls, start: ndarray, target: ndarray) -> 'Path':
        if start.size != 2 or start.size != 2:
            raise ValueError('Cannot create a path with less then two points')
        return cls(Position.from_array(start), Position.from_array(target))

    @classmethod
    def from_sequence(cls, points_list: Sequence[Position]) -> 'Path':
        if len(points_list) < 2:
            raise ValueError('Cannot create a path with less then two points')
        path = cls(start=Position(), target=Position())
        path.points = points_list
        return path

    @property
    def start(self) -> Position:
        return self[0]

    @start.setter
    def start(self, v: Position):
        self[0] = v

    @property
    def target(self) -> Position:
        return self[-1]

    @target.setter
    def target(self, v: Position):
        self[-1] = v

    @property
    def next_position(self) -> Position:
        return self[1]

    def copy(self) -> 'Path':
        return Path.from_sequence(self.points)

    @property
    def length(self) -> float:
        segments = [(point - next_point).norm for point, next_point in zip(self, self[1:])]
        return sum(segments)

    def __iter__(self) -> Position:
        for p in self.points:
            yield p

    def __getitem__(self, item) -> Position:
        return self.points[item]

    def __setitem__(self, key: int, value: Position):
        self.points[key] = value

    def __delitem__(self, key: int):
        del self.points[key]

    def insert(self, index, value):
        self.points.insert(index, value)

    def __len__(self) -> int:
        return len(self.points)

    def __add__(self, other) -> 'Path':
        return Path.from_sequence(self.points + other.points[1:])

    def __repr__(self) -> str:
        return 'Path(start={}, target={})'.format(self.start, self.target)

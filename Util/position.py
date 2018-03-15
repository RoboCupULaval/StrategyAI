# Under MIT License, see LICENSE.txt
from typing import Dict, List, Tuple, TypeVar, cast

import numpy as np

POSITION_ABS_TOL = 0.01

T = TypeVar('T', int, float)


class Position:

    def __init__(self, x: T=0, y: T=0):
        self._array = np.array([x, y])

    @classmethod
    def from_array(cls, array: np.ndarray) -> 'Position':
        if array.size != 2:
            raise ValueError('Position can only be create with a size 2 array.')
        return cls(array[0], array[1])

    @classmethod
    def from_list(cls, new_list: List[T]) -> 'Position':
        return cls(new_list[0], new_list[1])

    @classmethod
    def from_dict(cls, new_dict: Dict[str, T]) -> 'Position':
        return cls(new_dict['x'], new_dict['y'])

    @property
    def x(self) -> T:
        return self.array[0]

    @x.setter
    def x(self, x: T):
        self._array[0] = x

    @property
    def y(self) -> T:
        return self.array[1]

    @y.setter
    def y(self, y: T):
        self._array[1] = y

    @property
    def norm(self) -> T:
        return cast(T, np.sqrt(self.x ** 2 + self.y ** 2))

    @property
    def angle(self) -> T:
        return cast(T, np.arctan2(self.y, self.x))

    @property
    def array(self) -> np.ndarray:
        return self._array

    def to_dict(self) -> Dict[str, T]:
        return {'x': self.x, 'y': self.y}

    def to_tuple(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def copy(self) -> 'Position':
        return Position.from_array(self.array.copy())

    def __add__(self, other: 'Position') -> 'Position':
        return Position.from_array(self.array + other.array)

    def __sub__(self, other: 'Position') -> 'Position':
        return Position.from_array(self.array - other.array)

    def __mul__(self, other) -> 'Position':
        return Position.from_array(self.array * other)

    def __truediv__(self, other: 'Position') -> 'Position':
        return Position.from_array(self.array / other)

    def __neg__(self) -> 'Position':
        return Position.from_array(-self.array)

    def __eq__(self, other: 'Position') -> bool:
        return (self - other).norm < POSITION_ABS_TOL

    def __ne__(self, other: 'Position') -> bool:
        return not self.__eq__(other)

    def __getitem__(self, key: T) -> T:
        return self.array[key]

    def __setitem__(self, key: T, item: T):
        self.array[key] = item

    def __repr__(self) -> str:
        return 'Position' + str(self)

    def __str__(self) -> str:
        return '({:8.3f}, {:8.3f})'.format(self.x, self.y)

    def __hash__(self) -> int:
        return hash(str(self))


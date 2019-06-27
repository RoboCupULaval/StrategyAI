# Under MIT License, see LICENSE.txt
from typing import Dict, Tuple, Sequence
import math as m
import numpy as np

POSITION_ABS_TOL = 0.01


#pylint: disable=invalid-name, invalid-unary-operand-type
class Position:

    def __init__(self, x: float=0, y: float=0):
        self._array = np.array([x, y])

    @classmethod
    def from_array(cls, array: np.ndarray) -> 'Position':
        if array.size != 2:
            raise ValueError('Position can only be create with a size 2 array.')
        return cls(array[0], array[1])

    @classmethod
    def from_list(cls, new_list: Sequence[float]) -> 'Position':
        if len(new_list) < 2:
            raise ValueError('Position can only be create with a length 2 sequences.')
        return cls(new_list[0], new_list[1])

    @classmethod
    def from_dict(cls, new_dict: Dict[str, float]) -> 'Position':
        return cls(new_dict['x'], new_dict['y'])

    @classmethod
    def from_angle(cls, angle, norm=1) -> 'Position':
        return cls(norm * m.cos(angle), norm * m.sin(angle))

    @property
    def x(self) -> float:
        return self.array[0]

    @x.setter
    def x(self, x: float):
        self._array[0] = x

    @property
    def y(self) -> float:
        return self.array[1]

    @y.setter
    def y(self, y: float):
        self._array[1] = y

    @property
    def norm(self) -> float:
        return m.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def angle(self) -> float:
        return m.atan2(self.y, self.x)

    @property
    def array(self) -> np.ndarray:
        return self._array

    def to_dict(self) -> Dict[str, float]:
        return {'x': self.x, 'y': self.y}

    def to_tuple(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    @property
    def unit(self) -> 'Position':
        return self / self.norm

    def copy(self) -> 'Position':
        return Position.from_array(self.array.copy())

    def dot(self, p: 'Position') -> float:
        return self.array.dot(p.array)

    def flip_x(self):
        return Position(-self.x, self.y)

    def flip_y(self):
        return Position(self.x, -self.y)

    def __add__(self, other: 'Position') -> 'Position':
        return Position.from_array(self.array + other.array)

    def __radd__(self, other: 'Position') -> 'Position':
        return Position.from_array(self.array + other.array)

    def __sub__(self, other: 'Position') -> 'Position':
        return Position.from_array(self.array - other.array)

    def __rsub__(self, other: 'Position') -> 'Position':
        return Position.from_array(-self.array + other.array)

    def __mul__(self, other: float) -> 'Position':
        return Position.from_array(self.array * other)

    def __rmul__(self, other: float) -> 'Position':
        return Position.from_array(self.array * other)

    def __truediv__(self, other: float) -> 'Position':
        return Position.from_array(self.array / other)

    def __neg__(self) -> 'Position':
        return Position.from_array(-self.array)

    def __eq__(self, other: 'Position') -> bool:
        return (self - other).norm < POSITION_ABS_TOL

    def __ne__(self, other: 'Position') -> bool:
        return not self.__eq__(other)

    def __getitem__(self, key: int) -> float:
        return self.array[key]

    def __setitem__(self, key: int, value: float):
        self.array[key] = value

    def __repr__(self) -> str:
        return 'Position' + str(self)

    def __str__(self) -> str:
        return '({:8.3f}, {:8.3f})'.format(self.x, self.y)

    def __hash__(self) -> int:
        return hash(str(self))

import numpy as np


class Position(object):
    """ Vector with [x, y, z] """
    def __init__(self, x=0, y=0, z=0):
        assert(isinstance(x, (int, float))), 'x should be int or float.'
        assert(isinstance(y, (int, float))), 'y should be int or float.'
        assert(isinstance(z, (int, float))), 'z should be int or float.'

        self._array = np.array([float(x), float(y)])
        self.z = float(z)

    def copy(self):
        """
        copy() -> Position

        Return copy of Position.
        """
        return Position(self.x, self.y, self.z)

    # *** GETTER / SETTER ***
    def _getx(self):
        return float(self._array[0])

    def _setx(self, value):
        assert(isinstance(value, (int, float))), 'value should be Position or int or float.'
        self._array[0] = value

    """ Make self.x with setter and getter attributes """
    x = property(_getx, _setx)

    def _gety(self):
        return float(self._array[1])

    def _sety(self, value):
        assert(isinstance(value, (int, float))), 'value should be Position or int or float.'
        self._array[1] = value

    """ Make self.y with setter and getter attributes """
    y = property(_gety, _sety)

    # *** OPERATORS ***
    def __add__(self, other):
        """ Return self + other """
        if not isinstance(other, (Position, int, float)):
            return NotImplemented
        else:
            new_array = self._array + (other._array if isinstance(other, Position) else other)
            return Position(float(new_array[0]), float(new_array[1]))

    def __sub__(self, other):
        """ Return self - other """
        assert(isinstance(other, (Position, int, float))), 'other should be Position or int or float.'
        new_array = self._array - (other._array if isinstance(other, Position) else other)
        return Position(float(new_array[0]), float(new_array[1]))

    def __mul__(self, other):
        """ Return self * other """
        assert(isinstance(other, (Position, int, float))), 'other should be Position or int or float.'
        new_array = self._array * (other._array if isinstance(other, Position) else other)
        return Position(float(new_array[0]), float(new_array[1]))

    def __truediv__(self, other):
        """ Return self / other """
        assert(isinstance(other, (Position, int, float))), 'other should be Position or int or float.'
        new_array = self._array / (other._array if isinstance(other, Position) else other)
        return Position(float(new_array[0]), float(new_array[1]))

    def __eq__(self, other):
        """ Return self == other """
        assert(isinstance(other, Position)), 'other should be Position.'
        return (self._array == other._array).all()

    def __ne__(self, other):
        """ Return self != other """
        return not self.__eq__(other)

    def __str__(self):
        """ Return str(self) """
        return "(x={}, y={}, z={})".format(self._array[0], self._array[1], self.z)
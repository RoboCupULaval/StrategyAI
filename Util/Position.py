# Under MIT License, see LICENSE.txt

import math as m

POSITION_DELTA_TOLERANCE_MAGNITUDE = 1e1

class Position(object):
    """ Vector with [x, y, z] """
    def __init__(self, x=0, y=0, z=0):
        assert(isinstance(x, (int, float))), 'x should be int or float.'
        assert(isinstance(y, (int, float))), 'y should be int or float.'
        assert(isinstance(z, (int, float))), 'z should be int or float.'

        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def copy(self):
        """
        copy() -> Position

        Return copy of Position.
        """
        return Position(self.x, self.y, self.z)

    # *** OPERATORS ***
    def __add__(self, other):
        """ Return self + other """
        if not isinstance(other, (Position, int, float)):
            return NotImplemented
        else:
            new_x = self.x + (other.x if isinstance(other, Position) else other)
            new_y = self.y + (other.y if isinstance(other, Position) else other)
            return Position(new_x, new_y)

    def __sub__(self, other):
        """ Return self - other """
        if not isinstance(other, (Position, int, float)):
            raise NotImplementedError
        else:
            new_x = self.x - (other.x if isinstance(other, Position) else other)
            new_y = self.y - (other.y if isinstance(other, Position) else other)
            return Position(new_x, new_y)

    def __mul__(self, other):
        """ Return self * other """
        if not isinstance(other, (int, float)):
            raise NotImplementedError
        else:
            new_x = self.x * other
            new_y = self.y * other
            return Position(new_x, new_y)

    def __truediv__(self, other):
        """ Return self / other """
        if not isinstance(other, (int, float)):
            raise NotImplementedError
        else:
            new_x = self.x / other
            new_y = self.y / other
            return Position(new_x, new_y)

    def __eq__(self, other):
        """
            L'égalité est vérifié au niveau de l'unité.
            La comparison de float exige toujours un seuil de tolérance.
            Dans ce cas-ci, les décimales n'importent pas.
            Position(0.5, 0) == Position(0, 0) -> True
            (multiplication par la magnitude de tolérance, définie dans constant.py, puis conversion pour couper les décimales)
        """
        scaled_left_side_x = int(self.x * POSITION_DELTA_TOLERANCE_MAGNITUDE)
        scaled_right_side_x = int(other.x * POSITION_DELTA_TOLERANCE_MAGNITUDE)
        scaled_left_side_y = int(self.y * POSITION_DELTA_TOLERANCE_MAGNITUDE)
        scaled_right_side_y = int(other.y * POSITION_DELTA_TOLERANCE_MAGNITUDE)
        return scaled_left_side_x == scaled_right_side_x and scaled_left_side_y == scaled_right_side_y

    def __ne__(self, other):
        """ Return self != other """
        return not self.__eq__(other)

    def __repr__(self):
        """ Return str(self) """
        return "(x={}, y={}, z={})".format(self.x, self.y, self.z)

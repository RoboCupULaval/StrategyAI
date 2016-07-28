# Under MIT License, see LICENSE.txt


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
            raise NotImplemented
        else:
            new_x = self.x - (other.x if isinstance(other, Position) else other)
            new_y = self.y - (other.y if isinstance(other, Position) else other)
            return Position(new_x, new_y)

    def __mul__(self, other):
        """ Return self * other """
        if not isinstance(other, (int, float)):
            raise NotImplemented
        else:
            new_x = self.x * other
            new_y = self.y * other
            return Position(new_x, new_y)

    def __truediv__(self, other):
        """ Return self / other """
        if not isinstance(other, (int, float)):
            raise NotImplemented
        else:
            new_x = self.x / other
            new_y = self.y / other
            return Position(new_x, new_y)

    def __eq__(self, other):
        """ Return self == other """
        assert(isinstance(other, Position)), 'other should be Position.'
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        """ Return self != other """
        return not self.__eq__(other)

    def __repr__(self):
        """ Return str(self) """
        return "(x={}, y={}, z={})".format(self.x, self.y, self.z)

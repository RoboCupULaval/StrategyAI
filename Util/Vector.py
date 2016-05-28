#Under MIT License, see LICENSE.txt
import math as m
from ..Util.Position import Position
from ..Util.Pose import Pose


class Vector(object):
    def __init__(self, length=1.0, direction=0.0):
        """
        :param length: the vector's length
        :param direction: the vector's direction, in radians
        """
        assert (isinstance(length, (int, float))), 'length should be int or float value.'
        assert (isinstance(direction, (int, float))), 'direction should be int or float value.'

        x = length * m.cos(direction)
        y = length * m.sin(direction)
        self._attributes = [length, direction, x, y]

    # *** GETTER / SETTER ***
    def _getlength(self):
        return self._attributes[0]

    def _setlength(self, length):
        assert (isinstance(length, (int, float)))
        self._attributes[0] = length
        self._attributes[2] = length * m.cos(self._attributes[1])
        self._attributes[3] = length * m.sin(self._attributes[1])

    """ Make self.length with setter and getter attributes """
    length = property(_getlength, _setlength)

    def _getdirection(self):
        return self._attributes[1]

    def _setdirection(self, direction):
        assert (isinstance(direction, (int, float)))
        self._attributes[1] = direction
        self._attributes[2] = self._attributes[0] * m.cos(direction)
        self._attributes[3] = self._attributes[0] * m.sin(direction)

    """Make self.direction with setter and getter attributes """
    direction = property(_getdirection, _setdirection)

    def _getx(self):
        return self._attributes[2]

    def _setx(self, x):
        assert (isinstance(x, (int, float))), 'value should be Position or int or float.'
        self._attributes[2] = x
        self._attributes[0] = m.sqrt(x ** 2 + self._attributes[3] ** 2)
        self._attributes[1] = m.atan2(self._attributes[3], x)

    """ Make self.x with setter and getter attributes """
    x = property(_getx, _setx)

    def _gety(self):
        return self._attributes[3]

    def _sety(self, y):
        assert (isinstance(y, (int, float)))
        self._attributes[3] = y
        self._attributes[0] = m.sqrt(y ** 2 + self._attributes[2] ** 2)
        self._attributes[1] = m.atan2(y, self._attributes[2])

    """ Make self.y with setter and getter attributes """
    y = property(_gety, _sety)

    # *** OPERATORS ***
    def __eq__(self, other):
        """
        The == operator
        :param other: The comparison vector
        :return: A boolean stating whether the two Vectors are equal
        """
        assert (isinstance(other, Vector))
        #return self.length == other.length and self.direction == other.direction
        return round(self.length, 10) == round(other.length, 10) and round(self.direction, 10) == round(other.direction,
                                                                                                        10)

    def __ne__(self, other):
        """
        The != operator
        :param other: The comparison vector
        :return: A boolean stating whether the two Vectors are not equal
        """
        assert (isinstance(other, Vector))
        return not self.__eq__(other)

    def __add__(self, other):
        """
        The + operator
        :param other: A Position, a Pose or a Vector
        :return: An object of the same type as the input parameter other
        Note : if other is of type Pose, returns a new Pose whose orientation is the same as the current vector
        """
        assert (isinstance(other, (Position, Pose, Vector)))
        if isinstance(other, Position):
            return Position(other.x + self.x, other.y + self.y)
        elif isinstance(other, Pose):
            p = Position(other.position.x + self.x, other.position.y + self.y)
            return Pose(p, self.direction)
        elif isinstance(other, Vector):
            x = self.x + other.x
            y = self.y + other.y
            return Vector(m.sqrt(x ** 2 + y ** 2), m.atan2(y, x))

    def __radd__(self, other):
        """
        Allows commutativity for Position + Vector and Pose + Vector
        :param other: A Position or a Pose
        :return: An object of the same type as the input parameter other
        Note : if other is of type Pose, returns a new Pose whose orientation is the same as the current vector
        """
        assert (isinstance(other, (Position, Pose)))
        if isinstance(other, Position):
            return Position(other.x + self.x, other.y + self.y)
        elif isinstance(other, Pose):
            p = Position(other.position.x + self.x, other.position.y + self.y)
            return Pose(p, self.direction)

    def __iadd__(self, other):
        """
        The += operator
        :param other: A Vector to add to the current Vector
        :return: The current Vector is modified
        """
        assert (isinstance(other, Vector))
        x = self.x + other.x
        y = self.y + other.y
        self.length = m.sqrt(x ** 2 + y ** 2)
        self.direction = m.atan2(y, x)
        return self

    def __sub__(self, other):
        """
        The - operator
        :param other: A Vector
        :return: The new Vector resulting from the substraction
        """
        assert (isinstance(other, Vector))
        x = self.x - other.x
        y = self.y - other.y
        return Vector(m.sqrt(x ** 2 + y ** 2), m.atan2(y, x))

    def __isub__(self, other):
        """
        The -= operator
        :param other: A Vector to substract from the current Vector
        :return: The current Vector is modified
        """
        assert (isinstance(other, Vector))
        x = self.x - other.x
        y = self.y - other.y
        self.length = m.sqrt(x ** 2 + y ** 2)
        self.direction = m.atan2(y, x)
        return self

    def __neg__(self):
        """
        The unary arithmetic operation -
        :return: the opposite vector
        """
        return self.__mul__(-1)

    def __mul__(self, scalar):
        """
        Scalar Multiplication
        :param scalar: a real number
        :return: a new vector resulting of the scalar multiplication
        """
        assert (isinstance(scalar, (int, float)))
        if scalar >= 0:
            return Vector(length=scalar * self.length, direction=self.direction)
        else:
            return Vector(length=-1 * scalar * self.length, direction=-1 * self.direction)

    def __rmul__(self, scalar):
        """
        Allows commutativity for int*Vector
        :param scalar: a real number
        :return: a new vector resulting of the scalar multiplication
        """
        assert (isinstance(scalar, (int, float)))
        if scalar >= 0:
            return Vector(length=scalar * self.length, direction=self.direction)
        else:
            return Vector(length=-1 * scalar * self.length, direction=-1 * self.direction)

    def __imul__(self, scalar):
        """
        Incremental scalar multiplication
        :param scalar: a real number
        :return: the current resized vector
        """
        assert(isinstance(scalar, (int, float)))
        if scalar >= 0:
            self.length *= scalar
        else:
            self.length *= -1 * scalar
            self.direction *= -1
        return self

    def __str__(self):
        """
        :return: A string containing the Vector's attribute in a readable form
        """
        return "(Length = {}, Direction = {})".format(self.length, self.direction)

    # *** GENERAL METHODS ***
    def dot(self, vector):
        """
        The dot product
        :param vector: The second Vector of the dot product
        :return: The result of the dot product in a float
        """
        return self.length * vector.length * m.cos(self.direction - vector.direction)

    def unit(self):
        """
        :return: A unit Vector whose direction is the same as the current Vector
        """
        return Vector(length=1, direction=self.direction)

    def normal(self, plus90=True):
        """
        :param plus90: A boolean stating if the direction of the normal Vector is equal to the direction of
        the current Vector plus pi/2 (True) or minus pi/2 (False)
        :return: A unit Vector perpendicular to the current Vector
        """
        if plus90:
            return Vector(length=1, direction=self.direction + m.pi / 2)
        else:
            return Vector(length=1, direction=self.direction - m.pi / 2)

    def getangle(self, vector):
        """
        :param vector: The Vector
        :return: The smallest angle between the two Vectors, in radians
        """
        return m.fabs(self.direction - vector.direction)

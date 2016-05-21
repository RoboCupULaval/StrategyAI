from ..Util.Position import Position
import math as m


class Pose(object):
    """  Container of position and orientation """
    def __init__(self, position=Position(), orientation=0.0):
        assert(isinstance(position, Position)), 'position should be Position object.'
        assert(isinstance(orientation, (int, float))), 'orientation should be int or float value.'

        self.position = position
        self.orientation = orientation
        if self.orientation >= m.pi:
            self.orientation -= 2 * m.pi
        elif self.orientation <= -m.pi:
            self.orientation += 2*m.pi

    def __str__(self):
        return '[{}, theta={}]'.format(self.position, self.orientation)
    def __repr__(self):
        return self.__str__()   

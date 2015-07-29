from ..Util.Position import Position


class Pose(object):
    """  Container of position and orientation """
    def __init__(self, position=Position(), orientation=0.0):
        assert(isinstance(position, Position)), 'position should be Position object.'
        assert(isinstance(orientation, (int, float))), 'orientation should be int or float value.'
        assert(0 <= orientation <= 360), 'orientation should be between 0 and 360 degrees'

        self.position = position
        self.orientation = orientation

    def __str__(self):
        return '[{}, theta={}]'.format(self.position, self.orientation)

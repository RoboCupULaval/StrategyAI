from ..Util.Position import Position


class Pose(object):
    """  Container of position and orientation """
    def __init__(self, position=Position(), orientation=0.0):
        assert(isinstance(position, Position)), 'position should be Position object.'
        assert(isinstance(orientation, (int, float))), 'orientation should be int or float value.'

        self.position = position
        self.orientation = orientation % 360

    def __str__(self):
        return '[{}, theta={}]'.format(self.position, self.orientation)

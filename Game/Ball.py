# Under MIT License, see LICENSE.txt
from ..Util.Position import Position
import math


class Ball():
    def __init__(self):
        self._position = Position()
        self.velocity = Position()

    @property
    def position(self):
        return self._position

    def set_position(self, pos, delta):
        if pos != self._position and delta != 0:
            self.velocity.x = (pos.x - self._position.x)/delta
            self.velocity.y = (pos.y - self._position.y)/delta
            # FIXME: hack
            #print(math.sqrt(self.velocity.x**2 + self.velocity.y**2))
            #print(delta)

            self._position = pos


from ..Util.Position import Position
import time


class Ball():
    def __init__(self):
        self._position = Position()
        self._last_time = time.time()
        self.velocity = Position()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        if pos != self._position:
            newtime = time.time()
            deltatime = newtime-self._last_time
            self.velocity.x = (pos.x - self._position.x)/deltatime
            self.velocity.y = (pos.y - self._position.y)/deltatime

            self._position = pos
            self._last_time = newtime


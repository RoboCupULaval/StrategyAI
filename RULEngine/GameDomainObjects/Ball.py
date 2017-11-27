# Under MIT License, see LICENSE.txt
from RULEngine.Util.Position import Position


class Ball:
    def __init__(self):
        self._position = Position()
        self._velocity = Position()

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value) -> None:
        assert isinstance(value, Position)
        self._position = value

    @property
    def velocity(self) -> Position:
        return self._velocity

    @velocity.setter
    def velocity(self, value) -> None:
        assert isinstance(value, Position)
        self._velocity = value

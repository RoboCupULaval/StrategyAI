# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault"

from Util.Position import Position


class Ball:
    def __init__(self):
        self._position = Position()
        self._velocity = Position()

    def update(self, new_position: Position, new_velocity: Position):
        self.position = new_position
        self.velocity = new_velocity

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

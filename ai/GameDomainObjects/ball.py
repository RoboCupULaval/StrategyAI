# Under MIT License, see LICENSE.txt

from typing import Dict

from Util import Position


class Ball:

    def __init__(self, position=Position()):
        self._position = position
        self._velocity = Position()

    def update(self, new_dict: Dict):
        self.position = new_dict['position']
        self.velocity = new_dict['velocity']

    def is_moving_fast(self, fast_speed = 600.0): # mm/s
        return fast_speed < self.velocity.norm

    def is_mobile(self, immobile_speed = 300.0): # mm/s
        return immobile_speed < self.velocity.norm

    def is_immobile(self):
        return not self.is_mobile()

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value):
        assert isinstance(value, Position)
        self._position = value

    @property
    def velocity(self) -> Position:
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        assert isinstance(value, Position)
        self._velocity = value

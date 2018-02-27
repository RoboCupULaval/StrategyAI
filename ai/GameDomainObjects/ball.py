# Under MIT License, see LICENSE.txt

from typing import Dict

from Util import Position


class Ball:
    def __init__(self, id):
        self._id = id
        self._position = Position()
        self._velocity = Position()

    def update(self, new_position: Position, new_velocity: Position):
        self.position = new_position
        self.velocity = new_velocity

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value) -> None:
        assert isinstance(value, int)
        assert 0 <= value
        self._id = value

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

    @classmethod
    def from_dict(cls, ball_dict: Dict):
        b = Ball(ball_dict['id'])
        b.position = ball_dict['pose']
        b.velocity.x = ball_dict['velocity'].x
        b.velocity.y = ball_dict['velocity'].y
        return b

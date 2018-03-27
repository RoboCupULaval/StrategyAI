from enum import Enum


class Role(Enum):
    """Enum representing the role of one of our player playing on the field"""
    GOALKEEPER = 0
    MIDDLE = 1
    FIRST_DEFENCE = 2
    SECOND_DEFENCE = 3
    FIRST_ATTACK = 4
    SECOND_ATTACK = 5

    @classmethod
    def as_list(cls):
        return list(cls.__members__.values())  # Enum doesn't seems to support the iterable protocol

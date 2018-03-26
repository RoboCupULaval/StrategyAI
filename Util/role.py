from enum import Enum, auto


class Role(Enum):
    """Enum representing the role of one of our player playing on the field"""
    GOALKEEPER = auto()
    MIDDLE = auto()
    FIRST_DEFENCE = auto()
    SECOND_DEFENCE = auto()
    FIRST_ATTACK = auto()
    SECOND_ATTACK = auto()

    @classmethod
    def as_list(cls):
        return list(cls.__members__.values())  # Enum doesn't seems to support the iterable protocol

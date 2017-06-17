from enum import IntEnum

class Role(IntEnum):
    """Enum representing the role of one of our player playing on the field"""
    GOALKEEPER = 0
    FIRST_DEFENCE = 1
    SECOND_DEFENCE = 2
    MIDDLE = 3
    FIRST_ATTACK = 4
    SECOND_ATTACK = 5


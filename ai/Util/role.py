from enum import IntEnum

class Role(IntEnum):
    """Enum representing the role of one of our player playing on the field"""
    GOALKEEPER = 0
    MIDDLE = 1
    FIRST_DEFENCE = 2
    SECOND_DEFENCE = 3
    FIRST_ATTACK = 4
    SECOND_ATTACK = 5

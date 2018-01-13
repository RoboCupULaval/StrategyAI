from enum import IntEnum

class Role(IntEnum):
    """Enum representing the role of one of our player playing on the field"""
    GOALKEEPER = 1
    MIDDLE = 2
    FIRST_DEFENCE = 5
    SECOND_DEFENCE = 3
    FIRST_ATTACK = 4
    SECOND_ATTACK = 0

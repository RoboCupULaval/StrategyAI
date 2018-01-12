from enum import IntEnum

class Role(IntEnum):
    """Enum representing the role of one of our player playing on the field"""
    GOALKEEPER = 1
    MIDDLE = 0
    FIRST_DEFENCE = 5
    SECOND_DEFENCE = 3
    FIRST_ATTACK = 2
    SECOND_ATTACK = 3

# Under MIT License, see LICENSE.txt

from enum import Enum


class RefereeCommand(Enum):
    STOP = 0
    PLAY = 1
    HALF_TIME = 2
    KICKOFF = 3
    TIMEOUT = 4
    PENALTY_KICK = 5
    FREE_KICK = 6
    INDIRECT_FREE_KICK = 7
    THROW_IN = 8
    GOAL_KICK = 9
    CORNER_KICK = 10


class Referee:
    def __init__(self):
        self.command = RefereeCommand.STOP


class Stage():
    def __init__(self):
        pass


class Team():
    def __init__(self):
        pass

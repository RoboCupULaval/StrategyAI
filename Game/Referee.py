# Under MIT License, see LICENSE.txt

from enum import Enum


class RefereeCommand(Enum):
    STOP = 0
    HALT = 1


class Referee:
    def __init__(self):
        self.command = RefereeCommand.STOP


class Stage():
    def __init__(self):
        pass


class Team():
    def __init__(self):
        pass

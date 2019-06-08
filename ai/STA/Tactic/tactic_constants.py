# Under MIT license, see LICENSE.txt

from enum import Enum

""" Constantes concernant les tactiques. """


class Flags(Enum):
    INIT = 0
    WIP = 1
    FAILURE = 2
    SUCCESS = 3
    PASS_TO_PLAYER = 4


def is_complete(p_status_flag):
    return p_status_flag == Flags.FAILURE or p_status_flag == Flags.SUCCESS

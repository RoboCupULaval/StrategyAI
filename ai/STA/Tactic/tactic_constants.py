# Under MIT license, see LICENSE.txt
""" Constantes concernant les tactiques. """
# Flags
INIT = 0
WIP = 1
FAILURE = 2
SUCCESS = 3

DEFAULT_TIME_TO_LIVE = 0.5


def is_complete(p_status_flag):
    return p_status_flag == FAILURE or p_status_flag == SUCCESS

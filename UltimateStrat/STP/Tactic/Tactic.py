# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'

from abc import abstractmethod
from functools import wraps
from ... import InfoManager
from ....Util import geometry
from ..Skill import Action

class Tactique :
    def __init__(self, info_manager):
        self.info_manager = info_manager

    def exec(self):

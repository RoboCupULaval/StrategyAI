# Under MIT licence, see LICENCE.txt

__author__ = 'Robocup ULaval'


from abc import abstractmethod
from functools import wraps
from UltimateStrat import InfoManager
from Util import geometry

class Action:

    def __init__(self, info_manager):
        self.info_manager = info_manager

    def on_before(self):
        pass

    def on_after(self):
        pass

    def exec(self, joueur):
        return


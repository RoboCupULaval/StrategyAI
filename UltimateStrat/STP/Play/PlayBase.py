# Under MIT License, see LICENSE.txt
""" Module contenant la classe abstraite PlayBase """
from abc import abstractmethod

__author__ = 'RoboCupULaval'

class PlayBase:
    """ Un Play contients:
        + Une séquence de Tactic pour chaque robot.
        + Le PlayBook -> un dictionnaire {PlayName: Play object}
    """
    @abstractmethod
    def __init__(self, name='pBook'):
        self.name = name

    @abstractmethod
    def getTactics(self, index=None):
        """ Retourne la Tactic.

            :param index: L'index du robot, par défaut None.
            :return: list [TacticR0, TacticR1, ... , TacticR5]
        """
        pass

    def __getitem__(self, item):
        """
        :param item: str
        :return: Play
        """
        return self.getBook()[item]

    def getBook(self):
        """ Retourne le PlayBook

            :return: dict {'Play.__name__' = Play}
        """
        return dict(zip([cls.__name__ for cls in self.__class__.__subclasses__()],
                        self.__class__.__subclasses__()))

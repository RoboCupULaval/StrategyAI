# Under MIT License, see LICENSE.txt
from abc import ABCMeta , abstractmethod

__author__ = 'RoboCupULaval'


class Task(metaclass=ABCMeta):

    """Classe abstraite de base pour toutes les taches
    dans le behavior tree.

    Code original :
    http://magicscrollsofcode.blogspot.ca/2010/12/behavior-trees-by-example-ai-in-android.html
    """

    @abstractmethod
    def check_condition(self):
        """Regarde si la tache peut etre update
        @return True si elle peut, false si elle ne peut pas"""
        pass

    @abstractmethod
    def start(self):
        """Ajoute la logique de depart d'une tache"""
        pass

    @abstractmethod
    def end(self):
        """Ajoute la logique de fin d'une tache"""
        pass

    @abstractmethod
    def exec(self):
        """Specifie la logique que la tache doit actualisee
        a chaque cycle"""
        pass



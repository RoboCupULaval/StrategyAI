# Under MIT License, see LICENSE.txt
""" Module des Executor """
from abc import abstractmethod, ABCMeta

__author__ = 'RoboCupULaval'

class Executor(object, metaclass=ABCMeta):
    """ Classe abstraite des executeurs. À compléter. """

    def __init__(self, info_manager):
        self.info_manager = info_manager

    @abstractmethod
    def exec(self):
        """ Méthode qui sera appelé à chaque coup de boucle. """
        pass

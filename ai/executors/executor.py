# Under MIT License, see LICENSE.txt


from abc import ABCMeta, abstractmethod


class Executor(object, metaclass=ABCMeta):
    """ Classe abstraite des executeurs. """

    def __init__(self):
        pass

    @abstractmethod
    def exec(self):
        """ Méthode qui sera appelé à chaque coup de boucle. """
        pass

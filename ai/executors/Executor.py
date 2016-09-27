from abc import ABCMeta, abstractmethod


class Executor(object, metaclass=ABCMeta):
    """ Classe abstraite des executeurs. """

    def __init__(self):
        self.ws = None

    @abstractmethod
    def exec(self, p_world_state):
        """ Méthode qui sera appelé à chaque coup de boucle. """
        pass

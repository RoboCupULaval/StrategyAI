from abc import ABCMeta, abstractmethod


class Executor(object, metaclass=ABCMeta):
    """ Classe abstraite des executeurs. """

    def __init__(self, p_world_state):
        self.ws = p_world_state

    @abstractmethod
    def exec(self):
        """ Méthode qui sera appelé à chaque coup de boucle. """
        pass

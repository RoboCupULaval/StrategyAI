# Under MIT License, see LICENSE.txt


from abc import ABCMeta, abstractmethod

from ai.states.world_state import WorldState


class Executor(object, metaclass=ABCMeta):
    """ Classe abstraite des executeurs. """

    def __init__(self, p_world_state: WorldState):
        self.ws = p_world_state

    @abstractmethod
    def exec(self):
        """ Méthode qui sera appelé à chaque coup de boucle. """
        pass

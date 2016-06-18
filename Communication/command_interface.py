# Under MIT License, see LICENSE.txt
"""
    Défini une classe mère commune aux différents type de services d'envoies.
"""
from abc import ABCMeta, abstractmethod
from collections import deque
from ..Util.constant import DEBUG_RECEIVE_BUFFER_SIZE

class CommandSender(metaclass=ABCMeta):
    """ Interface pour les services d'envoies de commandes. """

    @abstractmethod
    def send_packet(self, packet):
        """ Envoie les paquets reçus en paramètres. """
        pass

class CommandReceiver(metaclass=ABCMeta):
    """ Interface pour les services de réceptions de commandes. """

    def __init__(self):
        self.packet_list = deque(maxlen=DEBUG_RECEIVE_BUFFER_SIZE)

    @abstractmethod
    def receive_packet(self):
        """ Logique nécessaire pour reçevoir les paquets. """
        pass

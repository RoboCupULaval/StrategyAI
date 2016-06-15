# Under MIT License, see LICENSE.txt
"""
    Défini une classe mère commune aux différents type de services d'envoies.
"""
from abc import ABCMeta, abstractmethod

class CommandSender(metaclass=ABCMeta):
    """ Classe mère, impose l'interface aux CommandSender. """

    @abstractmethod
    def send_packet(self, command):
        """ Fournit le service pour envoyer un type de paquet. """
        pass

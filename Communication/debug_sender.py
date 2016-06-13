"""
    Le module implémente les classes et la logique nécessaire pour envoyer les
    commandes au serveur de débogage.
"""
from ..Util.Exception import InvalidDebugType

class DebugCommand(object):
    """
       Classe qui encapsule selon le protocole de communication les informations
       à envoyer à l'interface de débogage.
       Implémente la version 1.0 du protocole.
    """

    def __init__(self):
        """ Constructeur, définie à vide les attributs nécessaires. """
        super().__init__()
        self.name = "ai"
        self.version = "v1.0"
        self.type_ = -1
        self.link = None
        self.data = None

    def _get_packet(self):
        """ Retourne le dictionnaire du paquet. """
        return {'name': self.name,
                'version': self.version,
                'type': self.type_,
                'link': self.link,
                'data': self.data}


    def get_packet(self):
        """
            Valide que les informations du paquets sont adéquates et retourne
            la représentation en dictionnaire du paquet.
        """
        if self.type_ == -1:
            raise InvalidDebugType("Le type de paquet de débogage est invalide.")
        return self._get_packet()

    def repr(self):
        """ Représentation: dictionnaire du paquet. """
        return str(self._get_packet())

def get_debug_packets(debug_manager):
    """
        Reçoit une instance du DebugManager de StrategyIA et retourne une liste
        de commande pour le serveur de débogage.

        :param debug_manager: Référence vers la façade de débogage pour obtenir
            les informations.
        :return: [DebugCommand, DebugCommand, ...]
    """
    # TODO: implémenter
    print("Not implemented yet.")
    print(str(debug_manager))

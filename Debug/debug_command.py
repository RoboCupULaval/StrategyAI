# Under MIT License, see LICENSE.txt

SENDER_NAME = "AI"


class DebugCommand(object):
    """
       Classe qui encapsule selon le protocole de communication les informations
       à envoyer à l'interface de débogage.
       Implémente la version 1.0 du protocole.
    """

    def __init__(self, p_type_, p_data, p_link=None, p_version="1.0"):
        """ Constructeur, définie à vide les attributs nécessaires. """
        super().__init__()
        self.name = SENDER_NAME
        self.version = p_version
        self.type_ = p_type_
        self.link = p_link
        self.data = p_data

    def _get_packet(self):
        """ Retourne le dictionnaire du paquet. """
        return {'name': self.name,
                'version': self.version,
                'type': self.type_,
                'link': self.link,
                'data': self.data}

    def get_packet_repr(self):
        """
            Valide que les informations du paquets sont adéquates et retourne
            la représentation en dictionnaire du paquet.
        """
        # FIXME commentary on that check, where does it comes from?
        if self.type_ == -1:
            raise InvalidDebugType("Le type de paquet de débogage est\
                                    invalide.")
        return self._get_packet()

    def unpack_command_from_raw_packet(self, p_raw_packet):
        """ Modifie les paramètres de la commande à ceux du paquet brute. """
        self.type_ = p_raw_packet['type']
        self.link = p_raw_packet['link']
        self.data = p_raw_packet['data']
        self.name = 'ui'

    def repr(self):
        """ Représentation: dictionnaire du paquet. """
        return str(self._get_packet())


class InvalidDebugType(Exception):
    """ Est levée si un paquet de débogage n'a pas le bon type. """
    pass


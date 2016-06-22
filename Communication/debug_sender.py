"""
    Le module implémente les classes et la logique nécessaire pour envoyer les
    commandes au serveur de débogage.
"""
from ..Util.Exception import InvalidDebugType
from ..Util.constant import SENDER_NAME, DEFAULT_DEBUG_TIMEOUT,\
                            DEFAULT_TEXT_ALIGN, DEFAULT_TEXT_COLOR,\
                            DEFAULT_TEXT_FONT, DEFAULT_TEXT_SIZE
from ..Util.DebugType import Point, Circle

class DebugCommand(object):
    """
       Classe qui encapsule selon le protocole de communication les informations
       à envoyer à l'interface de débogage.
       Implémente la version 1.0 du protocole.
    """

    def __init__(self, p_type_, p_link, p_data, p_version="v1.0"):
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


    def get_packet(self):
        """
            Valide que les informations du paquets sont adéquates et retourne
            la représentation en dictionnaire du paquet.
        """
        if self.type_ == -1:
            raise InvalidDebugType("Le type de paquet de débogage est\
                                    invalide.")
        return self._get_packet()

    def repr(self):
        """ Représentation: dictionnaire du paquet. """
        return str(self._get_packet())


def get_debug_packets(p_debug_manager):
    """
        Reçoit une instance du DebugManager de StrategyIA et retourne une liste
        de commande pour le serveur de débogage.

        :param debug_manager: Référence vers la façade de débogage pour obtenir
            les informations.
        :return: [DebugCommand, DebugCommand, ...]
    """
    commands = []
    # série de if stupide
    commands = commands + _get_log_packets(p_debug_manager)
    commands = commands + _get_draw_packets(p_debug_manager)
    commands = commands + _get_influence_map_packets(p_debug_manager)
    commands = commands + _get_text_packets(p_debug_manager)

    return map(_get_packet, commands)

def _get_log_packets(debug_manager):
    """
        Exécute la logique nécessaire pour construire les paquets de débogages
        concernant les journaux.
    """
    commands = []
    # log est un Log
    for log in debug_manager.get_logs():
        # on assume une structure en tuple (level, message)
        commands.append(DebugCommand(2, None, {'level': log.level,
                                               'message': log.message}))
    return commands

def _get_draw_packets(debug_manager):
    """
        Exécute la logique nécessaire pour construire les paquets de débogages
        concernant les figures à faire dessiner.
    """
    commands = []
    # figure_info est un FigureInfo
    for figure_info in debug_manager.get_draw():
        # strucuture générale
        figure, color = figure_info

        # s'il s'agit d'un point
        if figure is Point:
            data = {'point': (figure.x, figure.y),
                    'width': figure.width,
                    'color': (color.r, color.g, color.b),
                    'timeout': 0}
            commands.append(DebugCommand(3004, None, data))

        # s'il s'agit d'un cercle
        if figure is Circle:
            data = {'center': (figure.center.x, figure.center.y),
                    'radius': figure.radius,
                    'color': color,
                    'style': figure.style,
                    'is_fill': True,
                    'timeout': 0}
            commands.append(DebugCommand(3003, None, data))
    return commands

def _get_influence_map_packets(p_debug_manager):
    """
        Exécute la logique nécessaire pour construire les paquets de débogages
        concernant l'affichage des influences maps.
    """
    # TODO: implémenter la construction des paquets
    return []

def _get_text_packets(p_debug_manager):
    """
        Exécute la logique nécessaire pour construire les paquets de débogages
        concernant l'affichage des influences maps.
    """
    commands = []
    # TextInfo
    for txt in p_debug_manager.get_text():
        data = {'position': (txt.position.x, txt.position.y),
                'text': txt.text,
                'size': DEFAULT_TEXT_SIZE,
                'font': DEFAULT_TEXT_FONT,
                'align': DEFAULT_TEXT_ALIGN,
                'color': DEFAULT_TEXT_COLOR,
                'has_bold': False,
                'has_italic': False,
                'timeout': DEFAULT_DEBUG_TIMEOUT}
        commands.append(DebugCommand(3008, None, data))
    return commands

def _get_packet(p_cmd):
    """ Appel de la fonction pour récupérer le dictionnaire de commande. """
    return p_cmd.get_packet()

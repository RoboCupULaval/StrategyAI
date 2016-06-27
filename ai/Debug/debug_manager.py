# Under MIT License, see LICENSE.txt
"""
    Ce module expose un tableau blanc qui centralise l'information liée à
    l'interface de debug. Il est géré par l'infoManager.
"""
from collections import namedtuple

# TODO: refactor le module
def wrap_command(raw_command):
    command = DebugCommand(raw_command['type'], raw_command['link'], raw_command['data'])
    command.name = 'ui'
    return command

class DebugManager:
    """
        DebugManager représente un infoManager spécialisé dans la
        gestion des informations retournées par l'interface de
        debug.
    """

    def __init__(self):
        self.logs = []
        self.influence_map = []
        self.text = []
        self.draw = []

    def get_commands(self):
        commands = self._get_draw_commands()
        commands = commands + self._get_influence_map_commands()
        commands = commands + self._get_logs_commands()
        commands = commands + self._get_text_commands()
        return [c.get_packet_repr() for c in commands]

    def clear(self):
        self._clear_draw()
        self._clear_influence_map()
        self._clear_logs()

    def add_log(self, level, message):
        log = DebugCommand(2, None, {'level': level, 'message': message})
        self.logs.append(log)

    def add_point(self, x, y, width):
        data = {'point': (x, y),
                'width': width,
                'color': None,
                'timeout': 0}
        point = DebugCommand(3004, None, data)
        self.draw.append(point)

    def add_circle(self, center, radius, style):
        data = {'center': center,
                'radius': radius,
                'color': None,
                'style': style,
                'is_fill': True,
                'timeout': 0}
        circle = DebugCommand(3003, None, data)
        self.draw.append(circle)

    def add_influence_map(self, influence_map):
        # TODO implement
        pass

    def add_text(self, position, text, color):
        data = {'position': position,
                'text':text,
                'size': DEFAULT_TEXT_SIZE,
                'font': DEFAULT_TEXT_FONT,
                'align': DEFAULT_TEXT_ALIGN,
                'color': DEFAULT_TEXT_COLOR,
                'has_bold': False,
                'has_italic': False,
                'timeout': DEFAULT_DEBUG_TIMEOUT}
        text = DebugCommand(3008, None, data)
        self.text.append(text)

    def _get_logs_commands(self):
        return self.logs

    def _get_influence_map_commands(self):
        return self.influence_map

    def _get_text_commands(self):
        return self.text

    def _get_draw_commands(self):
        return self.draw
        self._clear_text()

    def _clear_logs(self):
        self.logs = []

    def _clear_influence_map(self):
        self.influence_map = []

    def _clear_text(self):
        self.text = []

    def _clear_draw(self):
        self.draw = []


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

    def get_packet_repr(self):
        """
            Valide que les informations du paquets sont adéquates et retourne
            la représentation en dictionnaire du paquet.
        """
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

# couleur rgb
Color = namedtuple('Color', 'r g b')

# Solarized color definition
YELLOW = Color(181, 137, 0)
ORANGE = Color(203, 75, 22)
RED = Color(220, 50, 47)
MAGENTA = Color(211, 54, 130)
VIOLET = Color(108, 113, 196)
BLUE = Color(38, 139, 210)
CYAN = Color(42, 161, 152)
GREEN = Color(133, 153, 0)

# Alias pour les identifiants des robots
COLOR_ID0 = YELLOW
COLOR_ID1 = ORANGE
COLOR_ID2 = RED
COLOR_ID3 = MAGENTA
COLOR_ID4 = VIOLET
COLOR_ID5 = BLUE

COLOR_ID_MAP = {0: COLOR_ID0,
                1: COLOR_ID1,
                2: COLOR_ID2,
                3: COLOR_ID3,
                4: COLOR_ID4,
                5: COLOR_ID5}

SENDER_NAME = "ai"
DEFAULT_DEBUG_TIMEOUT = 300 #ms
DEFAULT_TEXT_SIZE = 14 #px
DEFAULT_TEXT_FONT = 'Arial'
DEFAULT_TEXT_ALIGN = 'Left'
DEFAULT_TEXT_COLOR = Color(0, 0, 0)

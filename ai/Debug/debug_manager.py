# Under MIT License, see LICENSE.txt
"""
    Ce module expose un tableau blanc qui centralise l'information liée à
    l'interface de debug. Il est géré par l'infoManager.
"""
from collections import namedtuple


STRATEGY_COMMAND_TYPE = 5002
TACTIC_COMMAND_TYPE = 5003

class Color(object):
    # FIXME: hack
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def repr(self):
        return (self.r, self.g, self.b)

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
        self.commands = []
        self.ui_commands = []
        self.human_control = False

    def get_commands(self):
        packet_represented_commands = [c.get_packet_repr() for c in self.commands]
        self.commands = []
        return packet_represented_commands

    def get_ui_commands(self):
        cmds = self.ui_commands
        self.ui_commands = []
        return cmds

    def add_log(self, level, message):
        log = DebugCommand(2, None, {'level': level, 'message': message})
        self.commands.append(log)

    def add_point(self, point, color=VIOLET):
        data = {'point': point,
                'color': color.repr(),
                'width': 5,
                'timeout': 0}
        point = DebugCommand(3004, None, data)
        self.commands.append(point)

    def add_circle(self, center, radius):
        data = {'center': center,
                'radius': radius,
                'color': CYAN.repr(),
                'is_fill': True,
                'timeout': 0}
        circle = DebugCommand(3003, None, data)
        self.commands.append(circle)

    def add_line(self, start_point, end_point):
        data = {'start': start_point,
                'end': end_point,
                'color': MAGENTA.repr()}
        command = DebugCommand(3001, None, data)
        self.commands.append(command)

    def add_rectangle(self, top_left, bottom_right):
        data = {'top_left': top_left,
                'bottom_right': bottom_right,
                'color': YELLOW.repr(),
                'is_fill': True}
        command = DebugCommand(3006, None, data)
        self.commands.append(command)

    def add_influence_map(self, influence_map):
        data = {'field_data': influence_map,
                'coldest_color': BLUE.repr(),
                'hottest_color': RED.repr()}
        command = DebugCommand(3007, None, data)
        self.commands.append(command)

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
        self.commands.append(text)

    def add_ui_command(self, debug_command):
        self.human_control = True
        self.ui_commands.append(UIDebugCommand(debug_command))

    def add_odd_command(self, odd_cmd):
        self.commands.append(odd_cmd)

    def set_human_control(self, status=True):
        self.human_control = status

class DebugCommand(object):
    """
       Classe qui encapsule selon le protocole de communication les informations
       à envoyer à l'interface de débogage.
       Implémente la version 1.0 du protocole.
    """

    def __init__(self, p_type_, p_link, p_data, p_version="1.0"):
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

class UIDebugCommand(object):

    def __init__(self, raw_cmd):
        print(raw_cmd)
        self.data = raw_cmd['data']
        self.cmd_type = raw_cmd['type']

    def is_strategy_cmd(self):
        return self.cmd_type == STRATEGY_COMMAND_TYPE

    def is_tactic_cmd(self):
        return self.cmd_type == TACTIC_COMMAND_TYPE

class InvalidDebugType(Exception):
    """ Est levée si un paquet de débogage n'a pas le bon type. """
    pass

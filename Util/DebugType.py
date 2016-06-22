"""
    Le module définie une série de namedtuple pour aisément grouper les types
    de figures que l'IA peut envoyer à l'interface de débogage pour affichage.
"""
from collections import namedtuple

# log
Log = namedtuple('Log', 'level message')
# position en mm, width en px
Point = namedtuple('Point', 'x y width')
# un Point puis radius en px
Circle = namedtuple('Circle', 'center radius style')
# contenant un peu plus abstrait
FigureInfo = namedtuple('FigureInfo', 'figure color')
# contenant pour un texte
TextInfo = namedtuple('TextInfo', 'position text color')


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

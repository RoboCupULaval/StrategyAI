# Under MIT License, see LICENSE.txt
"""
    Ce module permet de créer des commandes pour faire agir les robots.
    Des fonctions utilitaire permettent de transformer une commande de
    Position (Pose) en une commande de vitesse.

    L'embarqué et le simulateur utilise un vecteur de vitesse (Pose) pour
    contrôler les robots.
"""

from ..Game.Player import Player
from ..Util.area import *


class _Command(object):
    def __init__(self, player):
        assert (isinstance(player, Player))
        self.player = player
        self.dribble = True
        self.dribble_speed = 10
        self.kick = False
        self.kick_speed = 0
        self.kick_charge = False
        self.is_speed_command = False
        self.pose = Pose()
        self.team = player.team
        self.stop_cmd = False


class Move(_Command):
    def __init__(self, player, destination, kick_charge=False):
        # Parameters Assertion
        assert (isinstance(player, Player)), "player doit etre un Player"
        assert (isinstance(destination, Pose))
        super().__init__(player)
        self.pose = destination
        self.kick_charge = kick_charge


class Kick(_Command):
    def __init__(self, player, kick_speed=0.5):
        """ Kick speed est un float entre 0 et 1 """
        assert (isinstance(player, Player))
        assert (isinstance(kick_speed, (int, float)))
        super().__init__(player)
        self.pose = Pose()
        self.kick = True
        self.kick_charge = False


class Stop(_Command):
    def __init__(self, player):
        assert (isinstance(player, Player))

        super().__init__(player)
        self.is_speed_command = True
        self.pose = Pose()
        self.stop_cmd = True



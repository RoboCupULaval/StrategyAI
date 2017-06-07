# Under MIT License, see LICENSE.txt
"""
    Ce module permet de créer des commandes pour faire agir les robots.
    Des fonctions utilitaire permettent de transformer une commande de
    Position (Pose) en une commande de vitesse.

    L'embarqué et le simulateur utilise un vecteur de vitesse (Pose) pour
    contrôler les robots.
"""
from abc import abstractmethod

import time

import threading

from ..Game.Player import Player
from ..Util.area import *
import RULEngine.Communication.util.serial_protocol as protocol
from pyhermes import McuCommunicator


class _Command(object):
    def __init__(self, player):
        assert (isinstance(player, Player))
        self.player = player
        self.pose = Pose()
        self.kick_speed = 0

    @abstractmethod
    def package_command(self):
        pass


class _ResponseCommand(_Command):
    def __init__(self, player, pause_cond: threading.Condition):
        super().__init__(player)
        self.pause_cond = pause_cond
        self.completed = False

    def wakeup_thread(self):
        # We don't want wake up
        with self.pause_cond:
            self.completed = True
            self.pause_cond.notify()

    def pause_thread(self):
        with self.pause_cond:
            if not self.completed:
                self.pause_cond.wait()


class GetBattery(_ResponseCommand):
    def __init__(self, player, pause_cond: threading.Condition):
        super().__init__(player, pause_cond)


class Move(_Command):
    def __init__(self, player, destination):
        # Parameters Assertion
        assert (isinstance(destination, Pose))
        super().__init__(player)
        self.pose = destination


class Kick(_Command):
    def __init__(self, player, kick_strength):
        """ Kick speed est un int entre 0 et 4 """
        # TODO FIXME KICK SPEED OR STRENGTH
        super().__init__(player)
        self.kick_speed = 4




class Stop(_Command):
    def __init__(self, player):
        super().__init__(player)



class ChargeKick(_Command):
    def __init__(self, player):
        super().__init__(player)


class Dribbler(_Command):
    def __init__(self, player, activate):
        super().__init__(player)
        self.dribbler_status = protocol.DribblerStatus.DISABLED
        if activate:
            self.dribbler_status = protocol.DribblerStatus.ENABLED


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

from ..Game.Player import Player
from ..Util.area import *
import RULEngine.Communication.util.serial_protocol as protocol


class _Command(object):
    def __init__(self, player):
        assert (isinstance(player, Player))
        self.player = player
        self.pose = Pose()
        self.kick_speed = 0

    @abstractmethod
    def package_command(self, mcu_version=protocol.MCUVersion.STM32F407):
        pass


class Move(_Command):
    def __init__(self, player, destination):
        # Parameters Assertion
        assert (isinstance(destination, Pose))
        super().__init__(player)
        self.pose = destination

    def package_command(self, mcu_version=protocol.MCUVersion.STM32F407):
        x = self.pose.position.x
        y = self.pose.position.y
        theta = self.pose.orientation
        if self.mcu_version == protocol.MCUVersion.C2000:
            x, y = x, -y

        player_idx = self.player.id
        packed_command = protocol.create_speed_command(x, y, theta, player_idx)

        if player_idx == 4:
            print("Command (x, y, t): {} -- {} -- {}".format(x, y, theta))

        return packed_command


class Kick(_Command):
    def __init__(self, player):
        """ Kick speed est un float entre 0 et 1 """
        super().__init__(player)
        self.kick_speed = 5

    def package_command(self, mcu_version=protocol.MCUVersion.STM32F407):
        return protocol.create_kick_command(self.player.id)


class Stop(_Command):
    def __init__(self, player):
        super().__init__(player)

    def package_command(self, mcu_version=protocol.MCUVersion.STM32F407):
        return protocol.create_speed_command(0, 0, 0, self.player.id)


class ChargeKick(_Command):
    def __init__(self, player):
        super().__init__(player)

    def package_command(self, mcu_version=protocol.MCUVersion.STM32F407):
        return protocol.create_charge_command(self.player.id)

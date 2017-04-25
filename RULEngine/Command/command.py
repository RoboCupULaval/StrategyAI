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
    def package_command(self):
        pass


class Move(_Command):
    def __init__(self, player, destination):
        # Parameters Assertion
        assert (isinstance(destination, Pose))
        super().__init__(player)
        self.pose = destination

    def package_command(self):
        x = self.pose.position.x
        y = self.pose.position.y
        theta = self.pose.orientation

        player_idx = self.player.id
        packed_command = protocol.create_speed_command(x, y, theta, player_idx)

        return packed_command


class Kick(_Command):
    def __init__(self, player, kick_strength):
        """ Kick speed est un int entre 0 et 4 """
        # TODO FIXME KICK SPEED OR STRENGTH
        super().__init__(player)
        self.kick_speed = 4

    def package_command(self):
        return protocol.create_kick_command(self.player.id, self.kick_speed)


class Stop(_Command):
    def __init__(self, player):
        super().__init__(player)

    def package_command(self):
        return protocol.create_speed_command(0, 0, 0, self.player.id)


class ChargeKick(_Command):
    def __init__(self, player):
        super().__init__(player)

    def package_command(self):
        print("Kick charge!")
        return protocol.create_charge_command(self.player.id)


class Dribbler(_Command):
    def __init__(self, player, activate):
        super().__init__(player)
        self.dribbler_status = protocol.DribblerStatus.DISABLED
        if activate:
            self.dribbler_status = protocol.DribblerStatus.ENABLED

    def package_command(self):
        print("Dribbler")
        if self.dribbler_status == protocol.DribblerStatus.DISABLED:
            status = 0
        else:
            status = 3
        return protocol.create_dribbler_command(self.player.id, status)

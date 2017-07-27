# Under MIT License, see LICENSE.txt
"""
    Ce module permet de créer des commandes pour faire agir les robots.
    Des fonctions utilitaire permettent de transformer une commande de
    Position (Pose) en une commande de vitesse.

    L'embarqué et le simulateur utilise un vecteur de vitesse (Pose) pour
    contrôler les robots.
"""
from abc import abstractmethod
import threading
from pyhermes import McuCommunicator

from RULEngine.Game.OurPlayer import OurPlayer
from RULEngine.Util.Pose import Pose


class Command(object):
    def __init__(self, player: OurPlayer):
        assert isinstance(player, OurPlayer)
        self.player = player
        # fixme Why does command need the speed???
        if player.ai_command is not None:
            self.cmd_repr = player.ai_command.speed

    @abstractmethod
    def package_command(self, mcu_communicator: McuCommunicator):
        pass


class ResponseCommand(Command):
    def __init__(self, player: OurPlayer, pause_cond: threading.Condition):
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

    def package_command(self, mcu_communicator: McuCommunicator):
        pass


class GetBattery(ResponseCommand):
    def __init__(self, player, pause_cond: threading.Condition):
        super().__init__(player, pause_cond)

    def package_command(self, mcu_communicator: McuCommunicator):
        return mcu_communicator.getBatterie(self.player.id)


class Move(Command):
    def __init__(self, player: OurPlayer):
        super().__init__(player)

    def package_command(self, mcu_communicator: McuCommunicator) -> None:
        mcu_communicator.sendSpeed(self.player.id,
                                   self.cmd_repr.position.x,
                                   self.cmd_repr.position.y,
                                   self.cmd_repr.orientation)


class Kick(Command):
    def __init__(self, player: OurPlayer):
        super().__init__(player)
        # TODO ask embedded for kick force integration MGL 2017/05/29
        self.kick_speed = self.player.ai_command.kick_strength

    def package_command(self, mcu_communicator: McuCommunicator) -> None:
        #print("kick sended")
        mcu_communicator.kick(self.player.id, self.kick_speed)


class Stop(Command):
    def __init__(self, player: OurPlayer):
        super().__init__(player)
        self.speed_repr = Pose()

    def package_command(self, mcu_communicator: McuCommunicator) -> None:
        mcu_communicator.sendSpeed(self.player.id, 0, 0, 0)


class StartChargingKick(Command):
    def __init__(self, player: OurPlayer):
        super().__init__(player)

    def package_command(self, mcu_communicator: McuCommunicator) -> None:
        mcu_communicator.charge(self.player.id)


class Dribbler(Command):
    def __init__(self, player: OurPlayer, activate: bool=True):
        super().__init__(player)
        self.activate = activate
        # todo ask embedded about dribbler strength MGL 2017/05/29

    def package_command(self, mcu_communicator: McuCommunicator) -> None:
        #if self.activate:
        mcu_communicator.turnOnDribbler(self.player.id)
        # else:
        #     mcu_communicator.turnOffDribbler(self.player.id)

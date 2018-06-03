# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from Engine.Communication.sender.sender_base_class import Sender
from Util.constant import KickForce, DribbleState


class SerialCommandSender(Sender):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self, packets_frame):

        for packet in packets_frame.packet:
            self.connection.sendSpeed(packet.robot_id,
                                      packet.command.x/1000,
                                      packet.command.y/1000,
                                      packet.command.orientation)

            if packet.kick_force is not KickForce.NONE:
                self.connection.kick(packet.robot_id, self.translate_kick_force(packet.kick_force))

            if packet.dribbler_state == DribbleState.FORCE_STOP:
                self.connection.turnOffDribbler(packet.robot_id)
            elif packet.dribbler_state == DribbleState.FORCE_SPIN:
                self.connection.turnOnDribbler(packet.robot_id)

            if packet.charge_kick:
                self.connection.charge(packet.robot_id)

    @staticmethod
    def translate_kick_force(kick_force: KickForce) -> int:
        kick_translation = {KickForce.NONE: 0,
                            KickForce.LOW: 1,
                            KickForce.MEDIUM: 3,
                            KickForce.HIGH: 5}
        return kick_translation[kick_force]
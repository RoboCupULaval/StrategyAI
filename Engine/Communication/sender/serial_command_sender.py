# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from Engine.Communication.sender.sender_base_class import Sender


class SerialCommandSender(Sender):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self, packets_frame):

        for packet in packets_frame.packet:

            self.connection.sendSpeed(packet.robot_id,
                                      packet.command.x/1000,
                                      packet.command.y/1000,
                                      packet.command.orientation)
            if packet.kick_force > 0:
                self.connection.kick(packet.robot_id, packet.kick_force)

            if packet.dribbler_active:
                self.connection.turnOnDribbler(packet.robot_id)

            if packet.charge_kick:
                self.connection.charge(packet.robot_id)

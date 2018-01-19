# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass


class SerialCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self):
        packet_frame = self.queue.get()
        for packet in packet_frame:
            self.connection.sendSpeed(packet.robot_id,
                                      packet.command['x']/1000,
                                      packet.command['y']/1000,
                                      packet.command['orientation'])


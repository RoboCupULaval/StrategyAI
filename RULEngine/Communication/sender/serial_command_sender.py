# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
import time


class SerialCommandSender(SenderBaseClass):

    send_sleep = 0.05

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self):

        packets_frame = self.queue.get()

        for packet in packets_frame.packet:
            cmd = packet.command
            if any(cmd.values()):
                self.connection.sendSpeed(packet.robot_id, cmd['x'] / 1000, cmd['y'] / 1000, cmd['orientation'])

        time.sleep(SerialCommandSender.send_sleep)

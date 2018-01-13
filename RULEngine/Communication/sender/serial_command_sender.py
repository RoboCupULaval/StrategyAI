# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass


class SerialCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self):
        packet = self.queue.get()
        for robot_id, cmd in packet.items():
            self.connection.sendSpeed(robot_id, cmd['x']/1000, cmd['y']/1000, cmd['orientation'])


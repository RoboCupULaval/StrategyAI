# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
import time


class SerialCommandSender(SenderBaseClass):

    buffer = {}
    last_sent_time = 0.0
    send_timeout = 0.050

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def send_packet(self):
        packets_frame = self.queue.get()
        for packet in packets_frame.packet:
            SerialCommandSender.buffer[packet.robot_id] = packet.command

        dt = time.time() - SerialCommandSender.last_sent_time
        if dt > SerialCommandSender.send_timeout:
            self.send_buffer()

    def send_buffer(self):
        for robot_id, cmd in SerialCommandSender.buffer.items():
            if not (cmd['x'] == cmd['y'] == 0):
                self.connection.sendSpeed(robot_id, cmd['x'] / 1000, cmd['y'] / 1000, cmd['orientation'])

        SerialCommandSender.buffer.clear()


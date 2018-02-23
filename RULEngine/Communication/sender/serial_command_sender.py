# Under MIT License, see LICENSE.txt

from pyhermes import McuCommunicator

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
import time

from threading import RLock, Thread
import sched


class SerialCommandSender(SenderBaseClass):

    buffer = {}
    send_delay = 0.050
    send_lock = RLock()
    send_thread = None

    def connect(self, connection_info):
        return McuCommunicator(timeout=0.1)

    def start(self):
        s = sched.scheduler(time.time, time.sleep)
        s.enter(SerialCommandSender.send_delay, 1, self.send_buffer, argument=(s,))
        SerialCommandSender.send_thread = Thread(target=s.run())
        SerialCommandSender.send_thread.start()
        super().start()

    def send_packet(self):
        packets_frame = self.queue.get()

        SerialCommandSender.send_lock.acquire()

        for packet in packets_frame.packet:
            SerialCommandSender.buffer[packet.robot_id] = packet.command

        SerialCommandSender.send_lock.release()

    def send_buffer(self, s):

        s.enter(SerialCommandSender.send_delay, 1, self.send_buffer, argument=(s,))

        SerialCommandSender.send_lock.acquire()

        for robot_id, cmd in SerialCommandSender.buffer.items():
            if any(cmd.values()):
                self.connection.sendSpeed(robot_id, cmd['x'] / 1000, cmd['y'] / 1000, cmd['orientation'])

        SerialCommandSender.buffer.clear()

        SerialCommandSender.send_lock.release()


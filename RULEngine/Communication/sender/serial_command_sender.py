# Under MIT License, see LICENSE.txt
import time
from collections import deque

from RULEngine.Command.command import *

COMMUNICATION_SLEEP = 0.001
MOVE_COMMAND_SLEEP = 0.05


class SerialCommandSender(object):
    def __init__(self):
        self.mcu_com = McuCommunicator(timeout=0.1)

        self.last_time = 0
        self.command_queue = deque()

        self.command_dict = {}

        self.terminate = threading.Event()
        self.comm_thread = threading.Thread(target=self.send_loop, name="SerialCommandSender")
        self.comm_thread.start()

    def send_loop(self):
        PACKET_FREQ = 50
        count = 0
        self.speed_time = time.time()
        while not self.terminate.is_set():
            if time.time() - self.last_time > MOVE_COMMAND_SLEEP:
                self.last_time = time.time()
                for _, next_command in self.command_dict.items():
                    if isinstance(next_command, Move):
                        count += 1
                        self._package_commands(next_command)
                        time.sleep(COMMUNICATION_SLEEP)
            else:
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    next_command = None
                if next_command:
                    count += 1
                    self._package_commands(next_command)
                time.sleep(COMMUNICATION_SLEEP)
            if count > PACKET_FREQ:
                timelapse = time.time() - self.speed_time
                self.speed_time = time.time()
                print("{} packets took {:3.2}s, this is {:3.2f} packet/s".format(count, timelapse, count/timelapse))
                count = 0

    def send_command(self, command: Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))

        if isinstance(command, Move) or isinstance(command, Stop):
            self.command_dict[command.player.id] = command
        else:
            self.command_queue.append(command)

    def send_responding_command(self, command: ResponseCommand):
        """
        Pause le thread appelant jusqu'à qu'une réponse est reçu
        """
        self.command_queue.append(command)
        command.pause_thread()

        return command.response

    def stop(self):
        self.terminate.set()
        self.comm_thread.join()

    def _package_commands(self, command: Command):
        response = command.package_command(self.mcu_com)

        if isinstance(command, ResponseCommand):
            command.response = response
            command.wakeup_thread()

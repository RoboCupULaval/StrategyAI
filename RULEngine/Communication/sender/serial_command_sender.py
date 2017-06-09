# Under MIT License, see LICENSE.txt
import threading
import time
from collections import deque
try:
    from pyhermes import McuCommunicator
except ImportError:
    print("Couldn't find the pyhermes package. Cannot send command to physical robots.",
          "\nTo remedy please run the command pip install -r requirements.txt")

from RULEngine.Command.command import Command

COMMUNICATION_SLEEP = 0.001


class SerialCommandSender(object):
    def __init__(self, baud_rate: int=115200):
        # todo see if we still need the baud_rate, ask embedded! MGL 2017/05/29
        self.mcu_communicator = McuCommunicator()
        self.command_queue = deque()
        self.terminate = threading.Event()
        self.comm_thread = threading.Thread(target=self.send_loop)
        self.comm_thread.start()

    def send_loop(self):
        while not self.terminate.is_set():
            if len(self.command_queue) > 100:
                print("Warning! high amount of queued serial commands to send")
                if len(self.command_queue) > 1000:
                    raise RuntimeError("command queue of serial command exceded 1000 back up commands")
            try:
                next_command = self.command_queue.popleft()
            except IndexError:
                next_command = None
            if next_command is not None:
                # print(next_command)
                next_command.package_command(self.mcu_communicator)
            time.sleep(COMMUNICATION_SLEEP)

    def send_command(self, command: Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))
        self.command_queue.append(command)

    def stop(self):
        self.terminate.set()
        self.comm_thread.join()
        self.terminate.clear()

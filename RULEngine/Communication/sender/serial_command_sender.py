# Under MIT License, see LICENSE.txt
import time
from collections import deque
try:
    from pyhermes import McuCommunicator
except ImportError:
    print("Couldn't find the pyhermes package. Cannot send command to physical robots.",
          "\nTo remedy please run the command pip install -r requirements.txt")

from RULEngine.Command.command import *


COMMUNICATION_SLEEP = 0.001
MOVE_COMMAND_SLEEP = 0.05


class SerialCommandSender(object):
    def __init__(self):
        self.mcu_com = McuCommunicator(timeout=0.1)

        self.last_time = 0
        self.command_queue = deque()

        self.command_dict = {0: Stop(OurPlayer(None, 0)), 1: Stop(OurPlayer(None, 1)), 2: Stop(OurPlayer(None, 2)),
                             3: Stop(OurPlayer(None, 3)), 4: Stop(OurPlayer(None, 4)), 5: Stop(OurPlayer(None, 5))}

        self.terminate = threading.Event()
        self.comm_thread = threading.Thread(target=self.send_loop)
        self.comm_thread.start()

    def send_loop(self):
        while not self.terminate.is_set():
            if time.time() - self.last_time > MOVE_COMMAND_SLEEP:
                try:
                    for next_command in self.command_dict.values():
                        # print(c)
                        self._package_commands(next_command)
                        time.sleep(COMMUNICATION_SLEEP)
                except RuntimeError as r:
                    # TODO FIXME this bug, happens when the dict gets changed inbetween loop because of the time.sleep
                    # possibly making thread switch and then we add a new entry in the command dict after an ia loop.
                    print("FIXME:",self.__class__.__name__)
                self.last_time = time.time()
            else:
                time.sleep(COMMUNICATION_SLEEP)
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    next_command = None
                if next_command:
                    self._package_commands(next_command)

    def send_command(self, command: Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))

        if isinstance(command, Move) or isinstance(command, Stop):
            self.command_dict[command.player.id] = command
        elif isinstance(command, Command):
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

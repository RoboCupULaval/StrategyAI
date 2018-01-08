# Under MIT License, see LICENSE.txt
import time
import logging
from multiprocessing import Process, Queue, Event

try:
    from pyhermes import McuCommunicator
except ImportError:
    print("Couldn't find the pyhermes package. Cannot send command to physical robots.",
          "\nTo remedy please run the command pip install -r requirements.txt")

from RULEngine.Command.command import *

COMMUNICATION_SLEEP = 0.001
MOVE_COMMAND_SLEEP = 0.05


class SerialCommandSender(Process):
    def __init__(self, robot_cmds_queue: Queue, stop_event: Event):
        super(SerialCommandSender, self).__init__()
        self.logger = logging.getLogger("SerialCommandSender")

        self.mcu_com = McuCommunicator(timeout=0.1)


    def _initialize(self):
        pass

    def run(self):
        pass

    def serve(self):
        pass

    def _stop(self):
        pass

    # TODO HERHE
"""
    def send_loop(self):
        def loop_send_packets(sc):
            if not self.terminate.is_set():
                sc.enter(MOVE_COMMAND_SLEEP, 1, loop_send_packets, (sc,))
            # Handle move commands
            for _, next_command in self.command_dict.items():
                if isinstance(next_command, Move):
                    self._package_commands(next_command)
                    time.sleep(COMMUNICATION_SLEEP)

            # Handle non-move commands
            while True:
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    break
                self._package_commands(next_command)

        sc = sched.scheduler(time.time, time.sleep)
        sc.enter(MOVE_COMMAND_SLEEP, 1, loop_send_packets, (sc,))
        sc.run()

    def send_command(self, command: Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))

        if isinstance(command, Move) or isinstance(command, Stop):
            self.command_dict[command.player.id] = command
        elif isinstance(command, Command):
            self.command_queue.append(command)

    def send_responding_command(self, command: ResponseCommand):
        self.command_queue.append(command)
        command.pause_thread()

        return command.response

    def stop(self):
        self.terminate.set()
        self.comm_thread.join()

    def _package_commands(self, command: Command):
        available_ids = [1, 2, 3, 4, 5, 6]
        if command.player.id in available_ids:
            response = command.package_command(self.mcu_com)

            if isinstance(command, ResponseCommand):
                command.response = response
                command.wakeup_thread()
"""
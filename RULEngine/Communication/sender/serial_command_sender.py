# Under MIT License, see LICENSE.txt
import os
import threading
import time
from collections import deque
from sys import platform

import serial
from serial.tools import list_ports

from RULEngine.Command.command import _Command, Move, Stop
from RULEngine.Game.Player import Player

COMMUNICATION_SLEEP = 0.001
MOVE_COMMAND_SLEEP = 0.05


class SerialCommandSender(object):
    def __init__(self, baud_rate=115200):

        port = _get_port()

        if platform.startswith('win'):
            self.serial = serial.Serial(port, baud_rate)
        else:
            self.serial = serial.Serial('/dev/' + port, baud_rate)

        self.last_time = 0
        self.command_queue = deque()

        # HACK
        self.command_dict = {0: Stop(Player(None, 0)), 1: Stop(Player(None, 1)), 2: Stop(Player(None, 2)),
                             3: Stop(Player(None, 3)), 4: Stop(Player(None, 4)), 5: Stop(Player(None,5))}

        self.terminate = threading.Event()
        self.comm_thread = threading.Thread(target=self.send_loop)
        self.comm_thread.start()

    def send_loop(self):
        while not self.terminate.is_set():
            if time.time() - self.last_time > MOVE_COMMAND_SLEEP:
                # print(self.command_dict)
                for c in self.command_dict.values():
                    packed_command = c.package_command()
                    self.serial.write(packed_command)
                    time.sleep(COMMUNICATION_SLEEP)
                self.last_time = time.time()
            else:
                time.sleep(COMMUNICATION_SLEEP)
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    next_command = None
                if next_command:
                    # print(next_command)
                    packed_command = next_command.package_command()
                    self.serial.write(packed_command)

    def send_command(self, command: _Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))

        # HACK
        # TODO fix me MGL 2017/03/13
        # FIXME please
        if isinstance(command, Move) or isinstance(command, Stop):
            self.command_dict[command.player.id] = command
        else:
            self.command_queue.append(command)

    def stop(self):
        self.terminate.set()
        self.comm_thread.join()
        self.terminate.clear()


def _get_port():
    serial_ports = []

    if platform.startswith('win'):
        serial_ports = [port.device for port in list_ports.comports()]
    else:
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("ttyUSB") or port.startswith(
                'ttyACM') or port.startswith("ttyBaseStation")]
    try:
        return serial_ports[0]
    except IndexError:
        raise Exception('No suitable serial port found.')

# Under MIT License, see LICENSE.txt
from sys import platform
from serial.tools import list_ports

import os
import threading
from enum import Enum
from collections import deque

import serial
import time

from RULEngine.Command.command import _Command, Move, Kick, ChargeKick, Stop, Dribbler
from RULEngine.Communication.util import serial_protocol as protocol
from RULEngine.Communication.util.serial_protocol import MCUVersion
from RULEngine.Game.Player import Player

SERIAL_DISABLED = -1
COMMUNICATION_SLEEP = 0.001
MOVE_COMMAND_SLEEP = 0.1


class SerialType(Enum):
    NRF = 1
    BLUETOOTH = 2


class SerialCommandSender(object):
    def __init__(self, port=None, baud_rate=115200, serial_type=SerialType.NRF, mcu_version=MCUVersion.STM32F407):

        self.mcu_version = mcu_version
        print("MCU: {} -- SERIAL: {}".format(mcu_version, serial_type))

        if not port:
            port = _get_port(serial_type)

        if platform.startswith('win'):
            self.serial = serial.Serial(port, baud_rate)
        else:
            self.serial = serial.Serial('/dev/' + port, baud_rate)
        self.mcu_version = mcu_version

        if self.mcu_version == MCUVersion.STM32F407 and serial_type == SerialType.BLUETOOTH:
            protocol.ping_robot(self.serial)

        self.type = serial_type
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
                print(self.command_dict)
                for c in self.command_dict.values():
                    packed_command = c.package_command(mcu_version=self.mcu_version)
                    self.serial.write(packed_command)
                self.last_time = time.time()
            else:
                time.sleep(COMMUNICATION_SLEEP)
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    next_command = None
                if next_command:
                    print(next_command)
                    packed_command = next_command.package_command(mcu_version=self.mcu_version)
                    self.serial.write(packed_command)
            """
            try:
                next_command = self.command_queue.popleft()
            except IndexError:
                next_command = None

            if next_command:
                packed_command = next_command.package_command(mcu_version=self.mcu_version)
                self.serial.write(packed_command)
            """

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


def _get_port(serial_type):
    serial_ports = []

    if platform.startswith('win'):
        serial_ports = [port.device for port in list_ports.comports()]
    else:
        if serial_type == SerialType.NRF:
            serial_ports = [port for port in os.listdir('/dev')
                            if port.startswith("ttyUSB") or port.startswith(
                    'ttyACM') or port.startswith("ttyBaseStation")]
        elif serial_type == SerialType.BLUETOOTH:
            serial_ports = [port for port in os.listdir('/dev')
                            if port.startswith("rfcomm")]
    try:
        # serial_ports[0]
        return serial_ports[0]
    except IndexError:
        raise Exception('No suitable serial port found.')

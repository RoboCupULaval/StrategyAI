# Under MIT License, see LICENSE.txt

import os
import threading
from enum import Enum
from collections import deque

import serial
import time

from cobs import cobs

from RULEngine.Command.command import _Command
from RULEngine.Communication.util import serial_protocol as protocol
from RULEngine.Communication.util.serial_protocol import MCUVersion

SERIAL_DISABLED = -1
COMMUNICATION_SLEEP = 0.05

class SerialType(Enum):
    NRF = 1
    BLUETOOTH = 2

class SerialCommandSender(object):
    def __init__(self, port=None, baud_rate=115200, serial_type=SerialType.NRF, mcu_version=MCUVersion.STM32F407):

        self.mcu_version = mcu_version
        print("MCU: {} -- SERIAL: {}".format(mcu_version, serial_type))

        if not port:
            port = _get_port(serial_type)

        self.serial = serial.Serial('/dev/' + port, baud_rate)
        self.mcu_version = mcu_version

        if self.mcu_version == MCUVersion.STM32F407 and serial_type == SerialType.BLUETOOTH:
            protocol.ping_robot(self.serial)

        self.type = serial_type
        self.last_time = 0
        self.command_queue = deque()
        self.comm_thread = threading.Thread(target=self.send_loop())
        self.terminate = threading.Event()

    def send_loop(self):
        while not self.terminate.is_set():
            time.sleep(COMMUNICATION_SLEEP)
            try:
                next_command = deque.popleft()
            except IndexError:
                next_command = None

            if next_command:
                packed_command = next_command.package_command(mcu_version=self.mcu_version)
                self.serial.write(packed_command)

    def send_command(self, command: _Command):
        self.command_queue.append(command)

    def stop(self):
        self.terminate.set()
        self.comm_thread.join()
        self.terminate.clear()


def _get_port(serial_type):
    serial_ports = []

    if serial_type == SerialType.NRF:
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("ttyUSB") or port.startswith(
                'ttyACM') or port.startswith("ttyBaseStation")]
    elif serial_type == SerialType.BLUETOOTH:
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("rfcomm")]
    try:
        serial_ports[0]
        return serial_ports[0]
    except IndexError:
        raise Exception('No suitable serial port found.')



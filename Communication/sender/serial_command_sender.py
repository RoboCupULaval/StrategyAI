# Under MIT License, see LICENSE.txt

import os
from enum import Enum

import serial
import time

from cobs import cobs

from RULEngine.Command.command import _Command
from RULEngine.Communication.util import serial_protocol as protocol
from RULEngine.Communication.util.serial_protocol import MCUVersion

SERIAL_DISABLED = -1

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

    def send_command(self, command: _Command):
        #print(command)
        packed_command = command.package_command(mcu_version=self.mcu_version)
        self.serial.write(packed_command)


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



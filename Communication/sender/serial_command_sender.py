# Under MIT License, see LICENSE.txt

import os
from enum import Enum

import serial
import time

from cobs import cobs

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

        if mcu_version == MCUVersion.STM32F407:
            protocol.ping_robot(self.serial)

        self.type = serial_type
        self.last_time = 0

    def send_command(self, command):
        x = command.pose.position.x
        y = command.pose.position.y
        if self.mcu_version == MCUVersion.C2000:
            x, y = x, -y

        player_idx = command.player.id
        sercommand = protocol.create_speed_command(x, y, 0, player_idx)
        # FIXME: hack bluetooth
        if self.type == SerialType.BLUETOOTH and player_idx == 4:
            now = time.time()
            delta = now - self.last_time
            print("({}) -- Command (x, y): {} -- {} -- {}".format(delta, x, y, command.pose.orientation))
            self.last_time = now
            self.serial.write(sercommand)
        else:
            self.serial.write(sercommand)


def _get_port(serial_type):
    serial_ports = []

    if serial_type == SerialType.NRF:
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("ttyUSB") or port.startswith(
                'ttyACM')]
    elif serial_type == SerialType.BLUETOOTH:
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("rfcomm")]
    try:
        serial_ports[0]
        return serial_ports[0]
    except IndexError:
        raise Exception('No suitable serial port found.')



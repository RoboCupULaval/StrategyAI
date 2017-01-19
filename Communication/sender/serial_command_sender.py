# Under MIT License, see LICENSE.txt

import os
import serial
import time

from cobs import cobs

from RULEngine.Communication.util import serial_protocol as protocol


class SerialCommandSender(object):
    def __init__(self, port=None, baud_rate=115200, serial_type="bluetooth"):
        if not port:
            port = _get_port(serial_type)

        self.serial = serial.Serial('/dev/' + port, baud_rate)
        if serial_type == "bluetooth":
            # TODO: faire une nouvelle classe pour gerer multiple connexion bluetooth et fichier config
            protocol.ping_robot(self.serial)

        self.type = serial_type

    def send_command(self, command):
        x = command.pose.position.x
        y = command.pose.position.y
        x, y = x, -y

        player_idx = command.player.id
        sercommand = protocol.create_speed_command(x, y, 0, player_idx)
        # FIXME: hack bluetooth
        if self.type == "rf" or player_idx == 3:
            self.serial.write(sercommand)


def _get_port(serial_type):
    serial_ports = []

    if serial_type == "rf":
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("ttyUSB") or port.startswith(
                'ttyACM')]
    elif serial_type == "bluetooth":
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("rfcomm")]
    try:
        serial_ports[0]
        return serial_ports[0]
    except IndexError:
        raise Exception('No suitable serial port found.')



# Under MIT License, see LICENSE.txt

import os
import serial

from RULEngine.Communication.util import serial_protocol as protocol


class SerialCommandSender(object):
    def __init__(self, port=None, baud_rate=115200, comm_type="bluetooth"):
        if not port:
            port = self._get_port(type)

        self.serial = serial.Serial('/dev/' + port, baud_rate)
        self.type = comm_type

    def send_command(self, command):
        x = command.pose.position.x
        y = command.pose.position.y
        x, y = x, -y

        player_idx = command.player.id
        sercommand = protocol.create_speed_command(x, y, 0, player_idx)
        # FIXME: hack bluetooth
        if self.type == "rf" or player_idx == 3:
            self.serial.write(sercommand)

    def _get_port(self, type):
        serial_ports = []

        if type == "rf":
            serial_ports = [port for port in os.listdir('/dev')
                            if port.startswith("ttyUSB") or port.startswith(
                    'ttyACM')]
        elif type == "bluetooth":
            serial_ports = [port for port in os.listdir('/dev')
                            if port.startswith("rfcomm")]
        try:
            print(serial_ports[0])
            return serial_ports[0]
        except IndexError:
            raise Exception('No suitable serial port found.')

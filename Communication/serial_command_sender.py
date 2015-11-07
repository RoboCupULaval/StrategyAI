#!/usr/bin/python
from .command_sender import CommandSender
from .serial_protocol import serial_protocol
import math
import os
import serial


class SerialCommandSender(CommandSender):

    def __init__(self, port=None, baudRate=115200):
        if not port:
            serial_ports = [port for port in os.listdir('/dev') if port.startswith("ttyUSB")]
            port = serial_ports[0]
        
        self.serial = serial.Serial('/dev/' + port, baudRate)

    #Can only send speed commands for now.
    #Can only send translation commands for now.
    def send_command(self, command):
        x = command.pose.position.x
        y = command.pose.position.y
        x, y = x, -y
        
        sercommand = bytearray(protocol.createSpeedCommand(x, y, 0, 0))
        ser.write(sercommand)
#!/usr/bin/python
from .command_sender import CommandSender
from .serial_protocol import serial_protocol
import math
import os
import serial
import time

protocol = serial_protocol()

class SerialCommandSender(CommandSender):
    
    def __init__(self, port=None, baudRate=115200):
        if not port:
            serial_ports = [port for port in os.listdir('/dev') if port.startswith("ttyUSB")]
            port = serial_ports[0]
        
        self.serial = serial.Serial('/dev/' + port, baudRate)
        self.last_time = time.time()
        

    #Can only send speed commands for now.
    #Can only send translation commands for now.
    def send_command(self, command):
        if command.player.id != 4: return
        if time.time() - self.last_time > 0.020:
            x = command.pose.position.x
            y = command.pose.position.y
            print(command.pose.position)
            x, y = x, -y
            
            sercommand = bytearray(protocol.createSpeedCommand(x, y, 0, 0))
            print(sercommand)
            self.serial.write(sercommand)
            self.last_time = time.time()
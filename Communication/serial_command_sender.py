#Under MIT License, see LICENSE.txt
#!/usr/bin/python
import serial
from . import serial_protocol as protocol
import math
import os

class SerialCommandSender(object):
    
    def __init__(self, port=None, baudRate=115200):
        if not port:
            serial_ports = [port for port in os.listdir('/dev')
                            if port.startswith("ttyUSB") or port.startswith('ttyACM')]
            try:
                port = serial_ports[0]
            except IndexError:
                raise Exception('No suitable serial port found.')
            
        self.serial = serial.Serial('/dev/' + port, baudRate)
        

    def send_command(self, command):
        x = command.pose.position.x
        y = command.pose.position.y
        x, y = x, -y
        
        sercommand = bytearray(protocol.create_speed_command(x, y, 0, command.player.id))
        self.serial.write(sercommand)

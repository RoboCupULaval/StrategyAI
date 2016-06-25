# Under MIT License, see LICENSE.txt

import struct

STARTBYTE = b'\x7E'
STOPBYTE = b'\x7F'
ESCAPEBYTE = b'\x7D'
SPEEDCOMMAND_ID = 1
PIDCOMMAND_ID = 2

def create_speed_command(x, y, theta, id):

    packet = struct.pack('<BBfff', id, SPEEDCOMMAND_ID, x, y, theta)

    return _pack_command(packet)


def _pack_command(command):

    command = command.replace(ESCAPEBYTE, ESCAPEBYTE+ESCAPEBYTE)
    command = command.replace(STARTBYTE, ESCAPEBYTE+STARTBYTE)
    command = command.replace(STOPBYTE, ESCAPEBYTE+STOPBYTE)

    return STARTBYTE + command + STOPBYTE

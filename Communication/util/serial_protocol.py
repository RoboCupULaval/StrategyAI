# Under MIT License, see LICENSE.txt

import struct
from cobs import cobs

C2000_STARTBYTE = b'\x7E'
C2000_STOPBYTE = b'\x7F'
C2000_ESCAPEBYTE = b'\x7D'
C2000_SPEEDCOMMAND_ID = 1
C2000_PIDCOMMAND_ID = 2

STM32_PROTOCOL_VERSION = 0x01
STM32_CMD_HEART_BEAT_REQUEST = 0x00
STM32_CMD_HEART_BEAT_RESPOND = 0x01
STM32_CMD_MOVEMENT_COMMAND = 0x02
STM32_CMD_SET_REGISTER = 0x03
STM32_CMD_ACK = 0x04
STM32_CMD_ROBOT_CRASHED_NOTIFICATION = 0x26
STM32_ADDR_BASE_STATION = 0xFE
STM32_ADDR_BROADCAST = 0xFF


def create_speed_command(x, y, theta, id, mcu_version="stm32"):
    # FIXME: Retirer la branche quand le MCU (microcontroleur) C2000 n'est
    # plus utilise
    packet = None
    if mcu_version == "c2000":
        packet = struct.pack('<BBfff', id, C2000_SPEEDCOMMAND_ID, x, y, theta)
        packet = bytearray(_pack_c2000_command(packet))
    elif mcu_version == "stm32":
        packet = _pack_stm32_cmd(x, y, theta)
    else:
        raise Exception("La version du protocole serial devrait etre 1 ou 2")

    return packet


def _pack_c2000_command(command):
    command = command.replace(C2000_ESCAPEBYTE, C2000_ESCAPEBYTE +
                              C2000_ESCAPEBYTE)
    command = command.replace(C2000_STARTBYTE,
                              C2000_ESCAPEBYTE + C2000_STARTBYTE)
    command = command.replace(C2000_STOPBYTE, C2000_ESCAPEBYTE + C2000_STOPBYTE)

    return C2000_STARTBYTE + command + C2000_STOPBYTE


def _pack_stm32_cmd(x, y, theta, destination_address=STM32_ADDR_BROADCAST):
    velocity = [x, y, theta]
    payload = struct.pack('%sf' % len(velocity), *velocity)
    header = bytes([STM32_PROTOCOL_VERSION,
                    STM32_ADDR_BASE_STATION,
                    destination_address,
                    STM32_CMD_MOVEMENT_COMMAND,
                    0x00])
    packet = payload + header

    return cobs.encode(bytes(packet)) + b'\0'

# Under MIT License, see LICENSE.txt

import struct
import time
from enum import Enum

from cobs import cobs

class MCUVersion(Enum):
    C2000 = 1
    STM32F407 = 2


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

SERIAL_TIMEOUT = 0.1


def create_speed_command(x, y, theta, id, mcu_version=MCUVersion.STM32F407):
    # FIXME: Retirer la branche quand le MCU (microcontroleur) C2000 n'est
    # plus utilise
    packet = None
    if mcu_version == MCUVersion.C2000:
        packet = struct.pack('<BBfff', id, C2000_SPEEDCOMMAND_ID, x, y, theta)
        packet = bytearray(_pack_c2000_command(packet))
    elif mcu_version == MCUVersion.STM32F407:
        velocity = [x, y, theta]
        packet = _stm32_pack_cmd(_stm32_pack_payload(velocity), STM32_CMD_MOVEMENT_COMMAND)
    else:
        raise Exception("La version du protocole serial devrait etre 1 ou 2")

    return packet


def ping_robot(serial):
    # ecriture de la commande de ping
    ping = _stm32_pack_ping()
    serial.write(ping)
    serial.flush()
    time.sleep(0.5)

    # TODO: extraire logique de lecture d'une commande
    # lecture de la reponse avec timeout
    start_time = time.time()
    buf = serial.read(1)
    while not b'\0' in buf:
        num_bytes_to_read = serial.inWaiting()
        if num_bytes_to_read > 0:
            buf += serial.read(1)
        elif (time.time() - start_time) > SERIAL_TIMEOUT:
            raise Exception("Serial timeout (aucun robot detecte probablement)")

    # decodage de la reponse
    response = ""
    if buf == "\0":
        response = "\0"
    else:
        buf = buf[0:-1]
        response = cobs.decode(buf)

    if len(response) < len(_stm32_generate_header()):
        raise Exception("Decodage de cobs a echoue pendant le ping d'init. (reponse invalide)")

    if response[3] == STM32_CMD_HEART_BEAT_RESPOND:
        print("Le robot a repondu au heartbeat!")


def _stm32_pack_ping():
    return _stm32_pack_cmd(0, STM32_CMD_HEART_BEAT_REQUEST)


def _pack_c2000_command(command):
    command = command.replace(C2000_ESCAPEBYTE, C2000_ESCAPEBYTE +
                              C2000_ESCAPEBYTE)
    command = command.replace(C2000_STARTBYTE,
                              C2000_ESCAPEBYTE + C2000_STARTBYTE)
    command = command.replace(C2000_STOPBYTE, C2000_ESCAPEBYTE + C2000_STOPBYTE)

    return C2000_STARTBYTE + command + C2000_STOPBYTE


def _stm32_pack_payload(data):
    return struct.pack('%sf' % len(data), *data)


def _stm32_pack_cmd(payload, cmd=STM32_CMD_MOVEMENT_COMMAND, destination_address=STM32_ADDR_BROADCAST):
    header = _stm32_generate_header(cmd, destination_address)

    packet = header

    if payload:
        packet += payload

    return cobs.encode(bytes(packet)) + b'\0'

def _stm32_generate_header(cmd=STM32_CMD_HEART_BEAT_REQUEST, destination_address=STM32_ADDR_BROADCAST):
    return bytes([STM32_PROTOCOL_VERSION,
                  STM32_ADDR_BASE_STATION,
                  destination_address,
                  cmd,
                  0x00])


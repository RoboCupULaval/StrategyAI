# Under MIT License, see LICENSE.txt

import struct
import time
from enum import Enum

from RULEngine.Util.cobs import cobs


STM32_PROTOCOL_VERSION = 0x01
STM32_CMD_HEART_BEAT_REQUEST = 0x00
STM32_CMD_HEART_BEAT_RESPOND = 0x01
STM32_CMD_MOVEMENT_COMMAND = 0x02
STM32_CMD_SET_REGISTER = 0x03
STM32_CMD_ACK = 0x04
STM32_CMD_ROBOT_CRASHED_NOTIFICATION = 0x26
STM32_REG_KICK = 0x01
STM32_REG_CHARGE_KICKER = 0x02
STM32_REG_DRIBBLER = 0x03
STM32_ADDR_BASE_STATION = 0xFE
STM32_ADDR_BROADCAST = 0xFF

SERIAL_TIMEOUT = 0.1


class DribblerStatus(Enum):
    DISABLED = 0
    ENABLED = 1


def create_speed_command(x, y, theta, robot_idx):
    velocity = [x, y, theta]
    packet = _stm32_pack_cmd(_stm32_pack_payload(velocity), STM32_CMD_MOVEMENT_COMMAND, robot_idx=robot_idx)
    return packet


def create_charge_command(robot_idx):
    return _create_register_command(STM32_REG_CHARGE_KICKER, 0, robot_idx)


def create_kick_command(robot_idx: int, kick_strength: int):
    return _create_register_command(STM32_REG_KICK, kick_strength, robot_idx)


def create_dribbler_command(robot_idx, status):
    return _create_register_command(STM32_REG_DRIBBLER, status, robot_idx)


def _create_register_command(register, value, robot_idx):
    payload = bytes([register, value])
    return _stm32_pack_cmd(payload, STM32_CMD_SET_REGISTER, robot_idx)


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


def _stm32_pack_payload(data):
    return struct.pack('%sf' % len(data), *data)


def _stm32_pack_cmd(payload, cmd=STM32_CMD_MOVEMENT_COMMAND, robot_idx=STM32_ADDR_BROADCAST):
    header = _stm32_generate_header(cmd, robot_idx)

    packet = header

    if payload:
        packet += payload

    checksum = bytes([sum(packet) & 0xff])
    packet = packet[:4] + checksum + packet[5:]
    return cobs.encode(bytes(packet)) + b'\0'


def _stm32_generate_header(cmd=STM32_CMD_HEART_BEAT_REQUEST, robot_idx=STM32_ADDR_BROADCAST):
    return bytes([STM32_PROTOCOL_VERSION,
                  STM32_ADDR_BASE_STATION,
                  robot_idx,
                  cmd,
                  0x00])


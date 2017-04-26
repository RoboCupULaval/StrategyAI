# Under MIT License, see LICENSE.txt
import os
import threading
import time
from collections import deque
from sys import platform

import serial
from serial.tools import list_ports
from pyhermes import McuCommunicator

from RULEngine.Command.command import _Command, Move, Stop, Kick, ChargeKick, Dribbler
from RULEngine.Game.Player import Player

COMMUNICATION_SLEEP = 0.001


class SerialCommandSender(object):
    def __init__(self, baud_rate=115200):
        self.McuCommunicator = McuCommunicator()

        """
        port = _get_port()

        if platform.startswith('win'):
            self.serial = serial.Serial(port, baud_rate)
        else:
            self.serial = serial.Serial('/dev/' + port, baud_rate)
        """

        self.last_time = 0
        self.command_queue = deque()

        # HACK
        self.command_dict = {0: Stop(Player(None, 0)), 1: Stop(Player(None, 1)), 2: Stop(Player(None, 2)),
                             3: Stop(Player(None, 3)), 4: Stop(Player(None, 4)), 5: Stop(Player(None,5))}

        self.terminate = threading.Event()
        self.comm_thread = threading.Thread(target=self.send_loop)
        self.comm_thread.start()

    def send_loop(self):
        while not self.terminate.is_set():
            if len(self.command_dict) > 0:
                for next_command in self.command_dict.values():
                    # print(c)
                    self._package_commands(next_command)
                    time.sleep(COMMUNICATION_SLEEP)
            else:
                time.sleep(COMMUNICATION_SLEEP)
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    next_command = None
                if next_command:
                    # print(next_command)
                    self._package_commands(next_command)

    def send_command(self, command: _Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))

        # HACK
        # TODO fix me MGL 2017/03/13
        # FIXME please
        if isinstance(command, Move) or isinstance(command, Stop):
            self.command_dict[command.player.id] = command
        else:
            self.command_queue.append(command)

    def stop(self):
        self.terminate.set()
        self.comm_thread.join()
        self.terminate.clear()

    def _package_commands(self, command: _Command):
        if isinstance(command, Move):
            x = command.pose.position.x
            y = command.pose.position.y
            theta = command.pose.orientation
            self.McuCommunicator.sendSpeed(command.player.id, x, y, theta)
        elif isinstance(command, Stop):
            self.McuCommunicator.sendSpeed(command.player.id, 0, 0, 0)
        elif isinstance(command, Kick):
            self.McuCommunicator.kick(command.player.id)
        elif isinstance(command, ChargeKick):
            self.McuCommunicator.charge(command.player.id)
        elif isinstance(command, Dribbler):
            if command.dribbler_status == 2:
                self.McuCommunicator.turnOnDribbler(command.player.id)
            else:
                self.McuCommunicator.turnOffDribbler(command.player.id)


"""
def _get_port():
    serial_ports = []

    if platform.startswith('win'):
        serial_ports = [port.device for port in list_ports.comports()]
    else:
        serial_ports = [port for port in os.listdir('/dev')
                        if port.startswith("ttyUSB") or port.startswith(
                'ttyACM') or port.startswith("ttyBaseStation")]
    try:
        return serial_ports[0]
    except IndexError:
        raise Exception('No suitable serial port found.')
"""
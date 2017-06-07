# Under MIT License, see LICENSE.txt
import os
import threading
import time
from collections import deque
from sys import platform

import serial
from serial.tools import list_ports
from pyhermes import McuCommunicator

from RULEngine.Command.command import _Command, _ResponseCommand
from RULEngine.Command.command import *
from RULEngine.Game.Player import Player

COMMUNICATION_SLEEP = 0.001
MOVE_COMMAND_SLEEP = 0.05


class SerialCommandSender(object):
    def __init__(self, baud_rate=115200):
        self.McuCommunicator = McuCommunicator()

        self.last_time = 0
        self.command_queue = deque()

        self.command_dict = {0: Stop(Player(None, 0)), 1: Stop(Player(None, 1)), 2: Stop(Player(None, 2)),
                             3: Stop(Player(None, 3)), 4: Stop(Player(None, 4)), 5: Stop(Player(None, 5))}

        self.terminate = threading.Event()
        self.comm_thread = threading.Thread(target=self.send_loop)
        self.comm_thread.start()

    def send_loop(self):
        while not self.terminate.is_set():
            if time.time() - self.last_time > MOVE_COMMAND_SLEEP:
                for next_command in self.command_dict.values():
                    # print(c)
                    self._package_commands(next_command)
                    time.sleep(COMMUNICATION_SLEEP)
                self.last_time = time.time()
            else:
                time.sleep(COMMUNICATION_SLEEP)
                try:
                    next_command = self.command_queue.popleft()
                except IndexError:
                    next_command = None
                if next_command:
                    self._package_commands(next_command)

    def send_command(self, command: _Command):
        # self.command_queue.append(command)
        # print("({}) Command deque length: {}".format(time.time(), len(self.command_queue)))

        if isinstance(command, Move) or isinstance(command, Stop):
            self.command_dict[command.player.id] = command
        else:
            self.command_queue.append(command)

    def send_responding_command(self, command: _ResponseCommand):
        """
        Pause le thread appelant jusqu'à qu'une réponse est reçu
        """
        self.command_queue.append(command)
        command.pause_thread()

        return command.response



    def stop(self):
        self.terminate.set()
        self.comm_thread.join()
        self.terminate.clear()

    def _package_commands(self, command: _Command,):
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
        elif isinstance(command, GetBattery):
            response = self.McuCommunicator.getBatterie(command.player.id)

        if isinstance(command, _ResponseCommand):
            command.response = response
            command.wakeup_thread()

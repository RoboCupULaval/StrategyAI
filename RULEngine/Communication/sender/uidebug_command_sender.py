# Under MIT License, see LICENSE.txt


import pickle

from RULEngine.Communication.sender.sender_base_class import SenderProcess
from RULEngine.Communication.sender.udp_socket import udp_socket
from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory

__author__ = "Maxime Gagnon-Legault"


class UIDebugCommandSender(SenderProcess):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self):

        try:
            cmds = self._queue.get()
            if not isinstance(cmds, list):
                cmds = [cmds]

            for cmd in cmds:
                self.connection.send(pickle.dumps(cmd))
        except ConnectionRefusedError:
            pass

    def send_robots_position(self, robots):
        for robot in robots:
            cmd1, cmd2 = UIDebugCommandFactory.robot(robot['pose'])
            self.connection.send(pickle.dumps(cmd1))
            self.connection.send(pickle.dumps(cmd2))

    def send_balls_position(self, balls):
        for ball in balls:
            cmd = UIDebugCommandFactory.ball(ball['pose'])
            self.connection.send(pickle.dumps(cmd))

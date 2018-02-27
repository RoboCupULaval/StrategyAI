# Under MIT License, see LICENSE.txt


import pickle

from RULEngine.Communication.sender.sender_base_class import SenderProcess
from RULEngine.Communication.sender.udp_socket import udp_socket
from RULEngine.Communication.monitor import monitor_queue

from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory


__author__ = "Maxime Gagnon-Legault"


@monitor_queue
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


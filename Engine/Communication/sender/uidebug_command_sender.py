# Under MIT License, see LICENSE.txt


import pickle

from Engine.Communication.sender.sender_base_class import SenderProcess
from Engine.Communication.sender.udp_socket import udp_socket
from Engine.Communication.monitor import monitor_queue

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


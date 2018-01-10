# Under MIT License, see LICENSE.txt

import pickle

from RULEngine.Communication.sender.sender_base_class import SenderBaseClass
from RULEngine.Communication.util.udp_socket import udp_socket


class UIDebugCommandSender(SenderBaseClass):

    def connect(self, connection_info):
        return udp_socket(connection_info)

    def send_packet(self):
        try:
            self.connection.send(pickle.dumps(self.queue.get(block=False)))
        finally:
            self.connection.close()

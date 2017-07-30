# Under MIT License, see LICENSE.txt
"""
    Regroupe les services utilisant l'UDP pour la communication. Ceux-ci
    permettent l'envoie et la réceptions de paquets pour le débogage, ainsi que
    l'envoie des commandes aux robots au niveau des systèmes embarqués.
"""

from collections import deque
from socketserver import BaseRequestHandler

import time

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2, google
from RULEngine.Communication.util.threaded_udp_server import ThreadedUDPServer


class ProtobufPacketReceiver(object):
    """
        Service qui implémente un serveur multicast UDP avec comme type de
        paquets ceux défini par la SSL en utilisant protobuf. Le serveur est
        async.
    """

    def __init__(self, host, port, packet_type):
        self.packet_list = deque(maxlen=100)
        handler = self.get_udp_handler(self.packet_list, packet_type)
        self.server = ThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, packet_list, packet_type):
        class ThreadedUDPRequestHandler(BaseRequestHandler):

            def handle(self):
                try:
                    data = self.request[0]
                    packet = packet_type()
                    packet.ParseFromString(data)
                    packet_list.append(packet)
                except google.protobuf.message.DecodeError:
                    print("fuck you")
                    pass

        return ThreadedUDPRequestHandler

    # TODO change the typing here in case of refereeMGL 2017/02/24
    def pop_frames(self)->messages_robocup_ssl_wrapper_pb2:
        """ Retourne une frame de la deque. """
        new_list = list(self.packet_list)

        self.packet_list.clear()
        return new_list

    # TODO change the typing here in case of referee MGL 2017/02/24
    def get_latest_frame(self)->messages_robocup_ssl_wrapper_pb2:
        """ Retourne sans erreur la dernière frame reçu. """
        try:
            return self.packet_list[-1]
        except IndexError:
            return None



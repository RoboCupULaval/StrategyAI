# Under MIT License, see LICENSE.txtRefereeReceiver
"""
    Regroupe les services utilisant l'UDP pour la communication. Ceux-ci
    permettent l'envoie et la réceptions de paquets pour le débogage, ainsi que
    l'envoie des commandes aux robots au niveau des systèmes embarqués.
"""
import logging
from queue import Queue, Full
from socketserver import BaseRequestHandler, UDPServer

import time

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2
from RULEngine.Communication.util.threaded_udp_server import ThreadedUDPServer
from google.protobuf.message import DecodeError


class ProtobufPacketReceiver(object):
    """
        Service qui implémente un serveur multicast UDP avec comme type de
        paquets ceux défini par la SSL en utilisant protobuf. Le serveur est
        async.
    """

    def __init__(self, host: str, port: int, packet_type, packet_queue: Queue):
        self.logger = logging.getLogger(__name__)
        self.packet_type = packet_type
        self.packet_list = packet_queue
        handler = self.get_udp_handler(self.packet_list, packet_type)
        self.server = ThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, packet_list, packet_type):
        class ThreadedUDPRequestHandler(BaseRequestHandler):

            def handle(self):
                try:
                    data = self.request[0]
                    packet = packet_type()
                    packet.ParseFromString(data)
                    packet_list.put(packet, block=True, timeout=0.1)
                except DecodeError:
                    print("Error parsing receiving packet, maybe you are listening to the wrong port?")
                    raise
                except Full:
                    logging.error("ThreadeUDPSrver with packet type {0} couldn't put a new packet within 0.1s".
                                  format(packet_type))

        return ThreadedUDPRequestHandler

    def pop_frames(self):
        """ Retourne une frame de la deque. """
        new_list = list(self.packet_list)

        return new_list

    def get_latest_frame(self):
        """ Retourne sans erreur la dernière frame reçu. """
        try:
            return self.packet_list.get(timeout=0.1)
        except Full:
            logging.error("ProtobufPacketReceiver with packet type {0} couldn't get a new packet within 0.1s".
                          format(self.packet_type))
            return None

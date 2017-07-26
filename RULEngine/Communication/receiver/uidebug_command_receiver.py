# Under MIT License, see LICENSE.txt

import pickle
from collections import deque
from socketserver import BaseRequestHandler

from RULEngine.Communication.util.threaded_udp_server import ThreadedUDPServer
from RULEngine.Util.constant import DEBUG_RECEIVE_BUFFER_SIZE
from config.config_service import ConfigService


class UIDebugCommandReceiver(object):
    """
        Service capable d'écouter un port multicast UDP, de reçevoir et de
        traiter les paquets brutes envoyer par le serveur de débogage.
    """
    def __init__(self):
        cfg = ConfigService()
        host = cfg.config_dict["COMMUNICATION"]["ui_debug_address"]
        port = int(cfg.config_dict["COMMUNICATION"]["ui_cmd_receiver_port"])
        self.packet_list = deque(maxlen=DEBUG_RECEIVE_BUFFER_SIZE)
        handler = self.get_udp_handler(self.packet_list)
        self.server = ThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, p_packet_list):
        """ Retourne la classe pour reçevoir async les paquets """

        class ThreadedUDPRequestHandler(BaseRequestHandler):
            """ Contient la logique pour traiter en callback une request. """
            def handle(self):
                """
                    Récupère la request et unpickle le paquet brute dans la
                    deque.
                """
                try:
                    data = self.request[0]
                    p_packet_list.append(pickle.loads(data))
                except:
                    pass
        return ThreadedUDPRequestHandler

    def receive_command(self):
        """ Vide la file et retourne une liste des paquets brutes. """
        for _ in range(len(self.packet_list)):
            yield self.packet_list.pop()
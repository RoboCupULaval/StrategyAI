from multiprocessing import Process, Event, Queue
from socketserver import BaseRequestHandler
from time import sleep

import pickle

from RULEngine.Communication.receiver.debug_command_receiver import DebugCommandReceiver
from RULEngine.Communication.util.threaded_udp_server import ThreadedUDPServer
from config.config_service import ConfigService


class DebugCommandReceiverCommunicationManager(Process):
    def __init__(self, debug_cmds_queue: Queue, stop_event: Event):
        super().__init__()

        cfg = ConfigService()
        self.host = cfg.config_dict["COMMUNICATION"]["ui_debug_address"]
        self.port = int(cfg.config_dict["COMMUNICATION"]["ui_cmd_receiver_port"])

        self.debug_cmds_queue = debug_cmds_queue
        self.handler = self.get_udp_handler(self.debug_cmds_queue)
        self.stop_event = stop_event
        self.server = None

    def initialize(self):
        self.server = ThreadedUDPServer(self.host, self.port, self.handler)

    def loop(self):
        pass

    def run(self):
        self.initialize()
        self.loop()

    def get_udp_handler(self, debug_cmds_queue):
        """ Retourne la classe pour reçevoir async les paquets """

        class ThreadedUDPRequestHandler(BaseRequestHandler):
            """ Contient la logique pour traiter en callback une request. """

            def handle(self):
                """
                    Récupère la request et unpickle le paquet brute dans la
                    deque.
                """
                data = self.request[0]
                debug_cmds_queue.append(pickle.loads(data))
        return ThreadedUDPRequestHandler

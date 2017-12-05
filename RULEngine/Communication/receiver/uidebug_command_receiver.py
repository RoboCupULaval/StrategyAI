# Under MIT License, see LICENSE.txt
import logging
import pickle
from multiprocessing import Process, Event, Queue
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, timeout


class UIDebugCommandReceiver(Process):
    TIME_OUT

    def __init__(self, host: str, port: int, uidebug_cmds_queue: Queue, stop_event: Event):
        super(UIDebugCommandReceiver, self).__init__()
        self.logger = logging.getLogger("VisionReceiver")
        self.host = host
        self.port = port

        self.socket = None

        self.uidebu_cmds_queue = uidebug_cmds_queue
        self.stop_event = stop_event

    def _initialize(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        if ip_address(self.host).is_multicast:
            self.socket.setsockopt(IPPROTO_IP,
                                   IP_ADD_MEMBERSHIP,
                                   pack("=4sl", inet_aton(self.host), INADDR_ANY))
        self.socket.settimeout(self.TIME_OUT)

        pass

    def run(self):
        pass

    def _stop(self):
        pass
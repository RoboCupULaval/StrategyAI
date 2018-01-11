# Under MIT License, see LICENSE.txt

__author__ = "Maxime Gagnon-Legault"

import logging
from multiprocessing import Process, Queue, Event
from socket import socket, AF_INET, SOCK_DGRAM, IPPROTO_IP, IP_ADD_MEMBERSHIP, inet_aton, INADDR_ANY, timeout
from queue import Full
from ipaddress import ip_address
from struct import pack
from pickle import loads


class UIDebugCommandReceiver(Process):
    TIME_OUT = 0.05

    def __init__(self, host: str, port: int, uidebug_cmds_queue: Queue, stop_event: Event):
        super(UIDebugCommandReceiver, self).__init__(name=__name__)
        self.logger = logging.getLogger("VisionReceiver")
        self.host = host
        self.port = port
        self.uidebug_cmds_queue = uidebug_cmds_queue
        self.stop_event = stop_event

        self.socket = None

    def _initialize(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        if ip_address(self.host).is_multicast:
            self.socket.setsockopt(IPPROTO_IP,
                                   IP_ADD_MEMBERSHIP,
                                   pack("=4sl", inet_aton(self.host), INADDR_ANY))
        self.socket.settimeout(self.TIME_OUT)
        self.logger.debug("Socket initialized")

    def run(self):
        self.logger.info('Starting process.')
        self._initialize()

        try:
            self._receive_packet()
        except KeyboardInterrupt:
            pass

        self._stop()

    def _receive_packet(self):
        while not self.stop_event.is_set():
            try:
                data, _ = self.socket.recvfrom(2048)
                self.uidebug_cmds_queue.put(loads(data))
            except Full as e:
                self.logger.debug("{}".format(e))
            except timeout:
                pass

    def _stop(self):
        self.logger.debug("has exited gracefully")
        exit(0)

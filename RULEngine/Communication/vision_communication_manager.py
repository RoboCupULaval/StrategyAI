import logging
import signal
from multiprocessing import Process, Event, Queue
from queue import Full
from time import sleep

import sys

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2 as ssl_wrapper
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver
from config.config_service import ConfigService


class VisionCommunicationManager(Process):
    def __init__(self, robot_cmds_queue: Queue, stop_event: Event):
        super().__init__()
        self.daemon = True
        cfg = ConfigService()
        self.host = cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        self.port = int(cfg.config_dict["COMMUNICATION"]["referee_port"])
        self.logger = logging.getLogger('VisionReceiver')
        self.robot_cmds_queue = robot_cmds_queue
        self.stop_event = stop_event
        self.server = None
        self.logger.debug("Vision initialized")
        print(self.pid)

    def initialize(self):
        self.server = ProtobufPacketReceiver(self.host, self.port, ssl_wrapper.SSL_WrapperPacket)
        print(self.server, " ", self.host, self.port)

    def loop(self):
        while not self.stop_event.is_set():
            cmd = self.server.get_latest_frame()
            try:
                if cmd is not None:
                    print(cmd)
                    self.robot_cmds_queue.put(cmd, False)
            except Full:
                pass  # todo Do something here maybe? MGL 2017/10/28
            sleep(0)
        return

    def run(self):
        print(self.pid)
        self.initialize()
        self.loop()

import logging
from multiprocessing import Process, Event, Queue as MQueue

from queue import Full, Queue
from time import sleep

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2 as ssl_wrapper
from RULEngine.Communication.util.protobuf_packet_receiver import ProtobufPacketReceiver
from config.config_service import ConfigService


class VisionCommunicationManager(Process):
    def __init__(self, vision_queue: MQueue, stop_event: Event):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # cfg = ConfigService()
        self.host = "224.5.23.2"   # cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        self.port = 10227  # int(cfg.config_dict["COMMUNICATION"]["referee_port"])

        self.vision_queue = vision_queue
        self.frame_queue = Queue(maxsize=100)

        self.stop_event = stop_event
        self.server = ProtobufPacketReceiver(self.host, self.port, ssl_wrapper.SSL_WrapperPacket, self.frame_queue)

        self.logger.debug("Vision Initialized")

    def loop(self):
        while not self.stop_event.is_set():
            cmd = self.frame_queue.get(block=True, timeout=0.1)
            print(cmd)
            try:
                if cmd is not None:
                    self.vision_queue.put(cmd, False)
            except Full:
                pass  # todo Do something here maybe? MGL 2017/10/28
            sleep(0.0001)

    def run(self):
        self.logger.debug("Vision started with pid {0}".format(1))
        self.loop()


if __name__ == "__main__":
    q = MQueue()
    e = Event()
    p = Process(target=VisionCommunicationManager, args=(q, e, ))
    print(p)
    p.start()
    print(p)
    while not e.is_set():
        print(q.get())

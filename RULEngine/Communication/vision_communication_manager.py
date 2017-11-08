import logging
from multiprocessing import Process, Event, Queue as MQueue
from queue import Queue, Full, Empty
from time import sleep

from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.trackbots.tracker.field import Field
from config.config_service import ConfigService


class VisionCommunicationManager(Process):
    def __init__(self, vision_queue: MQueue, stop_event: Event):
        super(VisionCommunicationManager, self).__init__()
        self.logger = logging.getLogger(__name__)

        # cfg = ConfigService()
        self.host = "224.5.23.2"   # cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        self.port = 10227  # int(cfg.config_dict["COMMUNICATION"]["referee_port"])

        self.vision_frame_queue = vision_queue
        self.observation_queue = Queue()

        self.stop_event = stop_event

        self.receiver = VisionReceiver(self.host, self.port, self.observation_queue)

        self.field = Field()
        self.logger.debug("Vision Initialized")

    def manage_vision(self):
        while True:
            try:
                self.observation_queue.get(block=True, timeout=0.5)
            except Full:
                self.logger.debug("Observation queue couldn't retrive within the time limit")
            except Empty:
                pass

    def run(self):
        self.logger.debug("Vision started with pid {0}".format(1))
        self.manage_vision()


if __name__ == "__main__":
    q = MQueue()
    e = Event()
    p = VisionCommunicationManager(q, e)
    print(p)
    p.start()
    print(p)
    print(p)
    sleep(0.1)
    print(p)
    while not e.is_set():
        print(q.get())
        print(p)

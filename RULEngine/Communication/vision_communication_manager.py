import logging
import threading
from multiprocessing import Process, Event, Queue
from queue import Full, Empty
from time import sleep

from config.config_service import ConfigService
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.trackbots.tracker.field import Field
from RULEngine.Communication.util.observations import BallObservation, RobotObservation, DetectionFrame


class VisionCommunicationManager(Process):
    def __init__(self, vision_queue: Queue, stop_event: Event):
        super(VisionCommunicationManager, self).__init__()
        self.logger = logging.getLogger("VisionCommunicationManager")

        cfg = ConfigService()
        self.host = cfg.config_dict["COMMUNICATION"]["referee_udp_address"]
        self.port = int(cfg.config_dict["COMMUNICATION"]["referee_port"])

        self.vision_frame_queue = vision_queue
        self.observation_queue = Queue()

        self.stop_event = stop_event
        self.server_stop_event = threading.Event()

        self.receiver = None

        self.field = Field()
        self.logger.debug("Vision Initialized")

    def initialize_server(self):
        self.receiver = VisionReceiver(self.host, self.port, self.observation_queue, self.server_stop_event)
        self.receiver.start()

    def manage_vision(self):
        while not self.stop_event.is_set():
            try:
                pass
                print(self.observation_queue.get())
                # print(self.receiver)
            except Full:
                pass
            except Empty:
                pass

        self.server_stop_event.set()

    def run(self):
        self.initialize_server()

        try:
            self.manage_vision()
        except KeyboardInterrupt:
            pass

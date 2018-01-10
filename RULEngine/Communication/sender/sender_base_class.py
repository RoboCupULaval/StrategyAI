from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Event
from queue import Empty, Queue
from typing import Tuple
import logging


class SenderBaseClass(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue, stop_event: Event):
        self.queue = queue
        self.stop_event = stop_event
        self.connection = self.connect(connection_info)
        super().__init__()
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def send_packet(self):
        pass

    def run(self):
        while not self.stop_event.is_set():
            try:
                self.send_packet()
            except Empty:
                pass


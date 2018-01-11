from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Event
from queue import Empty, Queue
from typing import Tuple
import logging


class SenderBaseClass(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue, stop_event: Event):
        super().__init__()
        self.queue = queue
        self.stop_event = stop_event
        self.connection = None
        self.connection_info = connection_info
        self.daemon = True
        self.logger = None

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def send_packet(self):
        pass

    def run(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = self.connect(self.connection_info)
        try:

            while not self.stop_event.is_set():
                self.send_packet()

        except KeyboardInterrupt:
            self.logger.info('Killed')
        finally:
            exit(0)


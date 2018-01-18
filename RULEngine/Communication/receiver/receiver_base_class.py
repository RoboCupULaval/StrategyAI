from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Event
from queue import Queue
from typing import Tuple
import logging


class ReceiverBaseClass(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue, stop_event: Event):
        super().__init__()

        self.queue = queue
        self.stop_event = stop_event
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = self.connect(connection_info)

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def receive_packet(self):
        pass

    def run(self):
        self.logger.info('Running')
        try:

            while not self.stop_event.is_set():
                self.receive_packet()
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info('Killed')

        exit(0)



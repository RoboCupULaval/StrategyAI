from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Event
from queue import Empty, Queue
from typing import Tuple
import logging


class SenderBaseClass(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue):
        super().__init__()
        self.queue = queue
        self.connection = self.connect(connection_info)
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def send_packet(self):
        pass

    def run(self):
        self.logger.debug('Running')
        try:
            while True:
                self.send_packet()
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.debug('Killed')

        exit(0)

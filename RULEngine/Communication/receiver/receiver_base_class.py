
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue
from multiprocessing.managers import DictProxy
from typing import Tuple, Union
import logging


class ReceiverBaseClass(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, link: Union[Queue, DictProxy]):
        super().__init__()

        self._link = link
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

        self.logger.debug('Running')

        try:
            while True:
                self.receive_packet()
        except KeyboardInterrupt:
            pass
        finally:
            self.connection.close()
            self.logger.debug('Killed')

        exit(0)
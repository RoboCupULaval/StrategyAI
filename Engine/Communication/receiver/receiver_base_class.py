import os
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue
from multiprocessing.managers import DictProxy
from typing import Tuple, Union
import logging


class ReceiverBaseClass(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def receive_packet(self):
        pass


class Receiver(ReceiverBaseClass, metaclass=ABCMeta):

    def __init__(self, connection_info):
        self.connection = self.connect(connection_info)
        self.logger = logging.getLogger(self.__class__.__name__)


class ReceiverProcess(Process, ReceiverBaseClass, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, link: Union[Queue, DictProxy]):
        super().__init__()

        self._link = link
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = self.connect(connection_info)

    def run(self):

        self.logger.debug('Running with process ID {}.'.format(os.getpid()))

        try:
            while True:
                self.receive_packet()
        except KeyboardInterrupt:
            pass
        except:
            self.logger.exception('An error occurred.')
            raise

    def terminate(self):
        self.connection.close()
        self.logger.debug('Terminated')
        super().terminate()

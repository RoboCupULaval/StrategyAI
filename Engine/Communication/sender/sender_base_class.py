import os
import socket
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue

from typing import Tuple
import logging


class SenderBaseClass(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def send_packet(self, *args, **kwargs):
        pass


class Sender(SenderBaseClass, metaclass=ABCMeta):

    def __init__(self, connection_info):
        self.connection = self.connect(connection_info)
        self.logger = logging.getLogger(self.__class__.__name__)


class SenderProcess(Process, SenderBaseClass, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue):
        super().__init__()
        self.connection = self.connect(connection_info)
        self._queue = queue
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.logger.debug('Running with process ID {}.'.format(os.getpid()))
        try:
            while True:
                self.send_packet()
        except KeyboardInterrupt:
            pass
        except:
            self.logger.exception('An error occurred.')
        finally:
            self.connection.close()
            self.logger.debug('Closed.')

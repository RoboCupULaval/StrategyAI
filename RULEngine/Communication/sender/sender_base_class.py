from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue

from typing import Tuple
import logging
import time
import sched
from threading import Thread


class SenderBaseClass(metaclass=ABCMeta):

    def __init__(self, connection_info):
        self.connection = self.connect(connection_info)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def send_packet(self, packet):
        pass


class SenderProcess(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue):
        super().__init__()
        self.connection = self.connect(connection_info)
        self._queue = queue
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def send_packet(self):
        pass

    def start(self):
        s = sched.scheduler(time.time, time.sleep)
        s.enter(1, 1, self.monitor_queue, argument=(s,))
        Thread(target=s.run, args=(s,), daemon=True).start()
        super().start()

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

    def monitor_queue(self, s):
        s.enter(1, 1, self.monitor_queue, argument=(s,))

        # noinspection PyProtectedMember
        usage = self._queue.qsize() / self._queue._maxsize

        if usage > 0.5:
            self.logger.debug('Queue is at {}% of it\'s max capacity.'.format(100 * usage))

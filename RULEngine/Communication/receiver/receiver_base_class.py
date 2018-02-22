from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue
from typing import Tuple
import logging
import sched
import time
from threading import Thread


class ReceiverBaseClass(Process, metaclass=ABCMeta):

    def __init__(self, connection_info: Tuple, queue: Queue):
        super().__init__()

        self._queue = queue
        self.daemon = True
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = self.connect(connection_info)

        s = sched.scheduler(time.time, time.sleep)
        s.enter(1, 1, self.monitor_queue, argument=(s,))
        self._monitoring_thread = Thread(target=s.run, args=(s,), daemon=True)

    @abstractmethod
    def connect(self, connection_info):
        pass

    @abstractmethod
    def receive_packet(self):
        pass

    def monitor_queue(self, s):
        s.enter(1, 1, self.monitor_queue, argument=(s,))

        usage = self._queue.qsize() / self._queue._maxsize

        if usage > 0.5:
            self.logger.debug('Queue is at {}% of it\'s max capacity.'.format(100 * usage))

    def start(self):
        super().start()
        self._monitoring_thread.start()
        self.logger.debug('Running')

    def run(self):

        try:
            while True:
                self.receive_packet()
        except KeyboardInterrupt:
            pass
        finally:
            self.connection.close()
            self.logger.debug('Killed')

        exit(0)

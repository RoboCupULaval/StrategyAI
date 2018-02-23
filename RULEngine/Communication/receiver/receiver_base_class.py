
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue
from multiprocessing.managers import DictProxy
from typing import Tuple, Union
import logging
import sched
import time
from threading import Thread


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


def monitor_queue(cls):

    class ReceiverWithQueueMonitoring:

        def __init__(self, *args, **kwargs):
            self.oInstance = cls(*args, **kwargs)
            s = sched.scheduler(time.time, time.sleep)
            s.enter(1, 1, self.monitor_queue, argument=(s,))
            Thread(target=s.run, args=(s,), daemon=True).start()

        def monitor_queue(self, s):
            s.enter(1, 1, self.monitor_queue, argument=(s,))

            # noinspection PyProtectedMember
            usage = self.oInstance._link.qsize() / self.oInstance._link._maxsize

            if usage > 0.5:
                self.oInstance.logger.debug('Queue is at {}% of it\'s max capacity.'.format(100 * usage))

        def __getattribute__(self, attr):
            try:
                x = super().__getattribute__(attr)
            except AttributeError:
                pass
            else:
                return x

            return self.oInstance.__getattribute__(attr)

    return ReceiverWithQueueMonitoring

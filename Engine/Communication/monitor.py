import sched
import time
from threading import Thread

from multiprocessing import Queue


def clear_queue(queue: Queue):
    size = queue.qsize()
    while size > 0:
        queue.get()
        size -= 1

def monitor_queue(cls):

    class QueueMonitor:

        def __init__(self, *args, **kwargs):
            self.oInstance = cls(*args, **kwargs)
            self.queue = args[1]
            s = sched.scheduler(time.time, time.sleep)
            s.enter(1, 1, self.monitor_queue, argument=(s,))
            Thread(target=s.run, args=(s,), daemon=True).start()

        def monitor_queue(self, s):
            s.enter(1, 1, self.monitor_queue, argument=(s,))

            usage = self.queue.qsize() / self.queue._maxsize

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

    return QueueMonitor

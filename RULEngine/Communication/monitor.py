import sched
import time
from threading import Thread


def monitor_queue(cls):

    class QueueMonitor:

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

    return QueueMonitor

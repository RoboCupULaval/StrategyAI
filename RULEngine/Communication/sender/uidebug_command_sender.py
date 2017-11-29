# Under MIT License, see LICENSE.txt
import logging
import pickle
from multiprocessing import Process, Queue, Event
from queue import Empty

from RULEngine.Communication.util.udp_socket import udp_socket


class UIDebugCommandSender(Process):
    def __init__(self, host: str, port: int, uidebug_queue: Queue, stop_event: Event):
        super(UIDebugCommandSender, self).__init__(name=__name__)
        self.logger = logging.getLogger("DebugCommandSender")

        self.host = host
        self.port = port
        self.socket = None

        self.stop_event = stop_event
        self.uidebug_queue = uidebug_queue

    def _initialize(self):
        self.socket = udp_socket(self.host, self.port)

        self.logger.debug("has initialized")

    def run(self):
        self._initialize()
        try:
            self._serve()
        except KeyboardInterrupt:
            pass

        self._stop()

    def _serve(self):
        while not self.stop_event.is_set():
            try:
                self.socket.send(pickle.dumps(self.uidebug_queue.get(block=False)))
            except ConnectionRefusedError:
                self.logger.error("connection refused to host {} with port {}. You might not be able to send debug "
                                  "command.".format(self.host, self.port))
            except Empty:
                pass
            except Exception as e:
                self.logger.debug(str(e))
                raise e


    def _stop(self):
        self.logger.debug("has exited.")
        exit(0)

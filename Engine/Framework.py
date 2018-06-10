# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Queue, Manager
import signal

import sys

from Engine.engine import Engine
from ai.coach import Coach
from Util.timing import create_fps_timer


class Framework:

    QUEUE_SIZE = 100
    CHECK_SUBPROCESS_STATE_IN_SECONDS = 2

    def __init__(self, profiling=False):

        self.logger = logging.getLogger(self.__class__.__name__)

        self.game_state = Manager().dict()
        self.field = Manager().dict()

        self.ai_queue = Queue(maxsize=Framework.QUEUE_SIZE)
        self.referee_queue = Queue(maxsize=Framework.QUEUE_SIZE)
        self.ui_send_queue = Queue(maxsize=Framework.QUEUE_SIZE)
        self.ui_recv_queue = Queue(maxsize=Framework.QUEUE_SIZE)

        self.engine = Engine(self.game_state,
                             self.field,
                             self.ai_queue,
                             self.referee_queue,
                             self.ui_send_queue,
                             self.ui_recv_queue)

        self.coach = Coach(self.game_state,
                           self.field,
                           self.ai_queue,
                           self.referee_queue,
                           self.ui_send_queue,
                           self.ui_recv_queue)

        if profiling:
            self.coach.enable_profiling()
            self.engine.enable_profiling()

    def start(self):

        self.engine.start()
        self.coach.start()

        signal.signal(signal.SIGINT, lambda *args: self.stop_game())
        sleep = create_fps_timer(Framework.CHECK_SUBPROCESS_STATE_IN_SECONDS)

        try:
            while self.engine.is_alive() and self.coach.is_alive():
                sleep()
        except SystemExit:
            self.logger.debug('One of the framework\'s subprocesses stopped. Shutting down...')
        finally:
            self.stop_game()

    def stop_game(self):
        self.engine.terminate()
        self.coach.terminate()
        sys.exit()


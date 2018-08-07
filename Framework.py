# Under MIT License, see LICENSE.txt

import logging
import os
import signal
from multiprocessing import Queue, Manager
import sys
import time

from Engine.engine import Engine
from ai.coach import Coach

from Util.timing import create_fps_timer

from config.config import Config
config = Config()


class Framework:

    QUEUE_SIZE = 100

    def __init__(self, profiling=False):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.profiling = profiling

        self.game_state = Manager().dict()
        self.field = Manager().dict()

        maxsize = config['FRAMEWORK']['max_queue_size']
        self.ai_queue = Queue(maxsize=maxsize)
        self.referee_queue = Queue(maxsize=maxsize)
        self.ui_send_queue = Queue(maxsize=maxsize)
        self.ui_recv_queue = Queue(maxsize=maxsize)

        self.engine = Engine(self)
        self.coach = Coach(self)

        self.watchdogs = {
            self.engine.name: Manager().Value('f', time.time()),
            self.coach.name:  Manager().Value('f', time.time())
        }

    def start(self):

        self.engine.start()
        self.coach.start()

        sleep = create_fps_timer(config['FRAMEWORK']['subprocess_check_time'])

        try:

            while self.coach.is_alive() and self.engine.is_alive():
                sleep()

        except SystemExit:
            pass
        except KeyboardInterrupt:
            self.logger.debug('Interrupted.')
        except BrokenPipeError:
            self.logger.exception('A connection was broken.')
        except:
            self.logger.exception('An error occurred.')
        finally:
            self.stop_game()

    def stop_game(self):
        self.logger.critical('Framework stopped.')

        try:
            os.kill(self.engine.pid, signal.SIGINT)
        except ProcessLookupError:
            pass

        try:
            os.kill(self.coach.pid, signal.SIGINT)
        except ProcessLookupError:
            pass
        
        sys.exit()

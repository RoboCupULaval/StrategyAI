# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Queue, Manager
import sys
from time import time

from Engine.engine import Engine
from ai.coach import Coach
from Util.timing import create_fps_timer


class Framework:

    QUEUE_SIZE = 100
    CHECK_SUBPROCESS_STATE_IN_SECONDS = 0.5
    MAX_HANGING_TIME = 3.0

    def __init__(self, profiling=False):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.profiling = profiling

        self.game_state = Manager().dict()
        self.field = Manager().dict()

        self.ai_queue = Queue(maxsize=Framework.QUEUE_SIZE)
        self.referee_queue = Queue(maxsize=Framework.QUEUE_SIZE)
        self.ui_send_queue = Queue(maxsize=Framework.QUEUE_SIZE)
        self.ui_recv_queue = Queue(maxsize=Framework.QUEUE_SIZE)

        self.engine_watchdog = Manager().Value('f', time())
        self.engine = Engine(self)

        self.coach_watchdog = Manager().Value('f', time())
        self.coach = Coach(self)

    def start(self):

        self.engine.start()
        self.coach.start()

        sleep = create_fps_timer(Framework.CHECK_SUBPROCESS_STATE_IN_SECONDS)

        try:
            while self.coach.is_alive() and self.engine.is_alive():
                sleep()

        except SystemExit:
            self.logger.debug('Terminated')
        except KeyboardInterrupt:
            self.logger.debug('A keyboard interrupt was raise.')
        except BrokenPipeError:
            self.logger.info('A connection was broken.')
        except:
            self.logger.exception('An error occurred.')

    def stop_game(self):
        self.logger.debug('Game stopped.')
        self.coach.join()
        self.coach_watchdog.close()
        self.engine.vision_state.close()
        self.engine.join(timeout=1)
        self.engine.ui_sender.join(timeout=1)
        self.engine.ui_recver.join(timeout=1)
        self.engine.referee_recver.join(timeout=1)
        self.game_state.close()
        self.field.close()
        self.engine_watchdog.close()
        #self.engine.join(timeout=1)
        sys.exit()

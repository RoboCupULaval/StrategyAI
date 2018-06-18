# Under MIT License, see LICENSE.txt
import logging
import os
import cProfile

from multiprocessing import Process
from queue import Full
from time import time, sleep

from Util.timing import create_fps_timer

from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState

from config.config import Config
config = Config()

class Coach(Process):

    MAX_EXCESS_TIME = 0.05

    def __init__(self, framework):

        super().__init__(name=__name__)

        self.framework = framework
        self.logger = logging.getLogger(self.__class__.__name__)

        # Managers for shared memory between process
        self.engine_game_state = self.framework.game_state
        self.field = self.framework.field

        # Queues for process communication
        self.ai_queue = self.framework.ai_queue
        self.referee_queue = self.framework.referee_queue
        self.ui_send_queue = self.framework.ui_send_queue
        self.ui_recv_queue = self.framework.ui_recv_queue

        # States
        self.game_state = GameState()
        self.play_state = PlayState()

        # Executors
        self.play_executor = PlayExecutor(self.play_state,
                                          self.ui_send_queue,
                                          self.referee_queue)
        self.debug_executor = DebugExecutor(self.play_state,
                                            self.play_executor,
                                            self.ui_send_queue,
                                            self.ui_recv_queue)

        # fps and limitation
        self.fps = config['GAME']['fps']
        self.frame_count = 0
        self.last_frame_count = 0
        self.dt = 0.0
        self.last_time = 0.0

        def callback(excess_time):
            if excess_time > Coach.MAX_EXCESS_TIME:
                self.logger.debug('Overloaded (%.1f ms behind schedule)', 1000*excess_time)

        self.fps_sleep = create_fps_timer(self.fps, on_miss_callback=callback)

        # profiling
        self.profiler = None

    def wait_for_geometry(self):
        self.logger.debug('Waiting for field\'s geometry from the Engine.')
        start = time()
        while not self.field:
            self.fps_sleep()
        self.game_state.const = self.field
        self.logger.debug('Geometry received from the Engine in {:0.2f} seconds.'.format(time() - start))

    def wait_for_referee(self):
        if Config()['GAME']['competition_mode']:
            self.logger.debug('Waiting for commands from the referee')
            while self.referee_queue.qsize() == 0:
                self.logger.debug('Referee is not active or port is set incorrectly, current port is {})'.format(
                    Config()['COMMUNICATION']['referee_port']))
                sleep(1)
            self.logger.debug('Referee command detected')

    def run(self):

        self.logger.debug('Running with process ID {} at {} fps.'.format(os.getpid(), self.fps))

        # profiling
        self.profiler = cProfile.Profile()
        if self.framework.profiling:
            self.profiler.enable()

        try:
            self.wait_for_geometry()
            self.wait_for_referee()
            while True:
                self.frame_count += 1
                self.update_time()
                self.main_loop()
                self.fps_sleep()
                self.framework.coach_watchdog.value = time()

        except KeyboardInterrupt:
            pass
        except BrokenPipeError:
            self.logger.exception('A connection was broken.')
        except:
            self.logger.exception('An error occurred.')
        finally:
            self.dump_profiling_stats()
            self.logger.info('Terminated')

    def main_loop(self):
        self.game_state.update(self.engine_game_state)
        self.debug_executor.exec()
        engine_commands = self.play_executor.exec()
        try:
            self.ai_queue.put_nowait(engine_commands)
        except Full:
            self.logger.critical('The Engine queue is full.')

    def update_time(self):
        current_time = time()
        self.dt = current_time - self.last_time
        self.last_time = current_time

    def dump_profiling_stats(self):
        if self.framework.profiling:
            self.profiler.dump_stats(config['GAME']['profiling_filename'])
            self.logger.debug('Profiling data written to {}.'.format(config['GAME']['profiling_filename']))

    def is_alive(self):
        if config['GAME']['competition_mode']:
            if time() - self.framework.coach_watchdog.value > self.framework.MAX_HANGING_TIME:
                self.logger.critical('Process is hanging. Shutting down.')
                return False
        return super().is_alive()

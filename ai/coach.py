# Under MIT License, see LICENSE.txt
import logging
import os
import cProfile

from multiprocessing import Process, Queue
from multiprocessing.managers import DictProxy
from time import time, sleep

from Util.timing import create_fps_timer

from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState

from config.config import Config
config = Config()

class Coach(Process):

    MAX_EXCESS_TIME = 0.1

    def __init__(self,
                 engine_game_state: DictProxy,
                 field: DictProxy,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):

        super().__init__(name=__name__)

        self.logger = logging.getLogger(self.__class__.__name__)

        # Managers for shared memory between process
        self.engine_game_state = engine_game_state
        self.field = field

        # Queues for process communication
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue

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

        def callback(excess_time):
            if excess_time > Coach.MAX_EXCESS_TIME:
                self.logger.debug('Overloaded (%.1f ms behind schedule)', 1000*excess_time)

        self.fps_sleep = create_fps_timer(self.fps, on_miss_callback=callback)

        # profiling
        self.profiling_enabled = False
        self.profiler = None

    def wait_for_geometry(self):
        self.logger.debug('Waiting for geometry from the Engine.')
        start = time()
        while not self.field:
            self.fps_sleep()
        self.game_state.const = self.field
        self.logger.debug('Geometry received from the Engine in {:0.2f} seconds.'.format(time() - start))

    def run(self) -> None:
        self.wait_for_geometry()

        self.logger.debug('Running with process ID {} at {} fps.'.format(os.getpid(), self.fps))
        try:
            while True:
                self.frame_count += 1
                self.main_loop()
                self.dump_profiling_stats()
                self.fps_sleep()
        except KeyboardInterrupt:
            pass

    def main_loop(self) -> None:
        self.game_state.update(self.engine_game_state)
        self.debug_executor.exec()
        engine_commands = self.play_executor.exec()
        self.ai_queue.put(engine_commands)

    def enable_profiling(self):
        self.profiling_enabled = True
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.logger.debug('Profiling mode activate.')

    def dump_profiling_stats(self):
        if self.profiling_enabled:
            if self.frame_count % (self.fps * config['GAME']['profiling_dump_time']) == 0:
                self.profiler.dump_stats(config['game']['profiling_filename'])
                self.logger.debug('Profiling data written to {}.'.format(config['game']['profiling_filename']))


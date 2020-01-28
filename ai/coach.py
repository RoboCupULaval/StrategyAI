# Under MIT License, see LICENSE.txt

from queue import Full
from time import time

from framework_process import FrameworkProcess

from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState

from config.config import Config

config = Config()


class Coach(FrameworkProcess):

    def __init__(self, framework):

        super().__init__(framework)

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
        self.engine_queue_full_timeout = None

    def wait_until_ready(self):

        self.logger.debug('Waiting for field\'s geometry from the Engine.')
        start = time()
        while not self.field:
            self.fps_sleep()
        self.game_state.const = self.field
        self.logger.debug(f'Geometry received from the Engine in {time() - start:.2f} seconds.')

        if config['COACH']['competition_mode']:
            self.logger.debug('Waiting for commands from the referee')
            while self.referee_queue.qsize() == 0:
                referee_port = config['COMMUNICATION']['referee_port']
                self.logger.debug(f'Referee is not active or port is set incorrectly, current port is {referee_port}')
                self.fps_sleep()
            self.logger.debug('Referee command detected')

    def main_loop(self):
        self.game_state.update(self.engine_game_state)
        self.debug_executor.exec()
        engine_commands = self.play_executor.exec()
        try:
            self.ai_queue.put_nowait(engine_commands)
        except Full:
            if self.engine_queue_full_timeout is None:
                self.engine_queue_full_timeout = time()
            if time() - self.engine_queue_full_timeout > 5:
                self.logger.critical('The Engine\'s queue was full for too long, the ai will crash.')
                raise
            self.logger.critical('The Engine\'s queue is full.')
            return
        self.engine_queue_full_timeout = None

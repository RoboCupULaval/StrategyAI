# Under MIT License, see LICENSE.txt
import logging
import os
from multiprocessing import Process, Queue
from multiprocessing.managers import DictProxy
from time import sleep, time
from typing import List

from Util.engine_command import EngineCommand
from Util.team_color_service import TeamColorService
from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class Coach(Process):

    def __init__(self,
                 engine_game_state: DictProxy,
                 field: DictProxy,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):

        super().__init__(name=__name__)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.cfg = ConfigService()

        cfg = ConfigService()
        self.mode_debug_active = cfg.config_dict['DEBUG']['using_debug'] == 'true'
        self.is_simulation = cfg.config_dict['GAME']['type'] == 'sim'

        # Managers for shared memory between process
        self.engine_game_state = engine_game_state
        self.field = field

        # Queues for interprocess communication with the engine
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue

        # the states
        self.team_color_service = TeamColorService()
        self.game_state = GameState()
        self.play_state = PlayState()

        # the executors
        self.play_executor = PlayExecutor(self.ui_send_queue)
        self.debug_executor = DebugExecutor(self.play_executor, self.ui_send_queue, self.ui_recv_queue)

    def wait_for_geometry(self):
        self.logger.debug('Waiting for geometry from the Engine.')
        start = time()
        while not self.field:
            sleep(0.1)
        self.logger.debug('Geometry received from the Engine in {:0.2f} seconds.'.format(time() - start))

    def run(self) -> None:
        own_pid = os.getpid()
        self.logger.debug('Running with process ID {}'.format(own_pid))
        self.wait_for_geometry()
        self.logger.debug('Running')
        try:
            while True:
                self.main_loop()
                sleep(0.05)  # TODO: Put it in config file

        except KeyboardInterrupt:
            pass

    def main_loop(self) -> None:
        self.game_state.update(self.engine_game_state)
        self.debug_executor.exec()
        engine_commands = self.play_executor.exec()
        self._send_cmd(engine_commands)

    def _send_cmd(self, engine_commands: List[EngineCommand]):
        self.ai_queue.put(engine_commands)

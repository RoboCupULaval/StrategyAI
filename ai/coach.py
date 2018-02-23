# Under MIT License, see LICENSE.txt
from typing import Dict, List

from Util.ai_command import AICommand


import logging
from multiprocessing import Process, Queue
from queue import Empty
from time import sleep

from RULEngine.services.team_color_service import TeamColorService
from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class Coach(Process):

    def __init__(self, engine_game_state: Dict, ai_queue: Queue, referee_queue: Queue,
                 ui_send_queue: Queue, ui_recv_queue: Queue):
        """
        Initialise l'IA.
        Celui-ci s'occupe d'appeler tout les morceaux de l'ia dans le bon ordre pour prendre une décision de jeu
        """
        super(Coach, self).__init__(name='Coach')

        self.logger = logging.getLogger(self.__class__.__name__)
        self.cfg = ConfigService()

        cfg = ConfigService()
        self.mode_debug_active = cfg.config_dict['DEBUG']['using_debug'] == 'true'
        self.is_simulation = cfg.config_dict['GAME']['type'] == 'sim'

        # Queues for interprocess communication with the engine
        self.engine_game_state = engine_game_state
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue

        # the states
        self.team_color_service = TeamColorService()
        self.game_state = None
        self.play_state = None

        # the executors
        self.debug_executor = None
        self.play_executor = None

    def initialize(self) -> None:
        self.game_state = GameState()
        self.play_state = PlayState()

        self.play_executor = PlayExecutor(self.ui_send_queue)
        self.debug_executor = DebugExecutor(self.play_executor, self.ui_send_queue, self.ui_recv_queue)

    def main_loop(self) -> None:
        sleep(1)
        while True:
            if self.engine_game_state:
                self.game_state.update(self.engine_game_state)
            self.debug_executor.exec()
            ai_commands = self.play_executor.exec()
            self._send_cmd(ai_commands)

            # TODO: Put it in config file
            sleep(0.05)

    def run(self) -> None:
        self.logger.debug('Running')

        self.initialize()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass

    def _send_cmd(self, ai_commands: List[AICommand]):
        self.ai_queue.put(ai_commands)

# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Process, Queue, Event

from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class Coach(Process):

    def __init__(self, game_state_queue: Queue, ai_queue: Queue, ui_send_queue: Queue, ui_recv_queue: Queue):
        """
        Initialise l'IA.
        Celui-ci s'occupe d'appeler tout les morceaux de l'ia dans le bon ordre pour prendre une décision de jeu
        """
        super(Coach, self).__init__(name=__name__)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.cfg = ConfigService()

        cfg = ConfigService()
        self.mode_debug_active = cfg.config_dict["DEBUG"]["using_debug"] == "true"
        self.is_simulation = cfg.config_dict["GAME"]["type"] == "sim"

        # Queues for interprocess communication with the engine
        self.game_state_queue = game_state_queue
        self.ai_queue = ai_queue
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue

        # the states
        self.game_state = None
        self.play_state = None

        # the executors
        self.debug_executor = None
        self.play_executor = None

    def initialize(self) -> None:
        self.game_state = GameState()
        self.play_state = PlayState()

        self.debug_executor = DebugExecutor(self.ui_recv_queue)
        # self.play_executor = PlayExecutor()

    def main_loop(self) -> None:
        while True:
            self.debug_executor.exec()
        # self.play_executor.exec()

    def run(self) -> None:
        self.initialize()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass

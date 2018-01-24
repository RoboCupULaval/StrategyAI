# Under MIT License, see LICENSE.txt

import logging
from multiprocessing import Process, Queue, Event
from time import sleep

from ai.executors.debug_executor import DebugExecutor
from ai.executors.play_executor import PlayExecutor
from ai.states.game_state import GameState
from ai.states.play_state import PlayState
from config.config_service import ConfigService


class Coach(Process):

    def __init__(self, game_state_queue: Queue, ai_queue: Queue, ui_send_queue: Queue, ui_recv_queue: Queue, stop_event: Event):
        """
        Initialise l'IA.
        Celui-ci s'occupe d'appeler tout les morceaux de l'ia dans le bon ordre pour prendre une décision de jeu
        """
        super(Coach, self).__init__(name=__name__)

        self.logger = logging.getLogger("Coach")
        self.cfg = ConfigService()

        cfg = ConfigService()
        self.mode_debug_active = cfg.config_dict["DEBUG"]["using_debug"] == "true"
        self.is_simulation = cfg.config_dict["GAME"]["type"] == "sim"

        # Queues for interprocess communication with the engine
        self.game_state_queue = game_state_queue
        self.ai_queue = ai_queue
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue

        # Event to know when to stop
        self.stop_event = stop_event

        # the states
        self.game_state = None
        self.play_state = None

        # the executors
        self.debug_executor = None
        self.play_executor = None

    def initialize(self) -> None:
        self.game_state = GameState()
        self.play_state = PlayState()

        # self.debug_executor = DebugExecutor()
        self.play_executor = PlayExecutor(self.ui_recv_queue)

    def main_loop(self) -> None:
        while not self.stop_event.is_set():
            last_game_state = self._get_last_game_state()
            # self.debug_executor.exec()
            self.play_executor.exec()
            sleep(0.05)

    def run(self) -> None:
        self.initialize()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass

    def _get_last_game_state(self):
        # This is a way to get the last available gamestate, it's probably should not be a queue
        size = self.game_state_queue.size()

        for _ in range(0, size -1):
            self.game_state_queue.pop()
        return self.game_state_queue.pop()

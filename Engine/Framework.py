# Under MIT License, see LICENSE.txt

import logging
import time
from argparse import Namespace
from multiprocessing import Queue, Manager
import signal  # so we can stop gracefully

from Engine.engine import Engine
from ai.coach import Coach
from config.config_service import ConfigService

__author__ = "Maxime Gagnon-Legault"


class Framework:
    """
        La classe contient la logique nécessaire pour communiquer avec
        les différentes parties(simulation, vision, uidebug et/ou autres),
         maintenir l'état du monde (jeu, referree, debug, etc...) et appeller
         l'ia.
    """

    def __init__(self, cli_args):
        """ Constructeur de la classe, établis les propriétés de bases et
        construit les objets qui sont toujours necéssaire à son fonctionnement
        correct.
        """

        # logger
        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Framework")

        # config
        self.cfg = ConfigService()

        # Managers
        self.game_state = Manager().dict()
        self.field = Manager().dict()

        # Queues
        self.ai_queue = Queue(maxsize=100)
        self.referee_queue = Queue(maxsize=100)
        self.ui_send_queue = Queue(maxsize=100)
        self.ui_recv_queue = Queue(maxsize=100)

        # Engine
        self.engine = Engine(self.game_state,
                             self.field,
                             self.ai_queue,
                             self.referee_queue,
                             self.ui_send_queue,
                             self.ui_recv_queue)

        self.engine.fps = cli_args.engine_fps
        if cli_args.unlock_engine_fps:
            self.engine.unlock_fps()

        self.engine.start()

        # AI
        self.coach = Coach(self.game_state,
                           self.field,
                           self.ai_queue,
                           self.referee_queue,
                           self.ui_send_queue,
                           self.ui_recv_queue)
        self.coach.start()

        # end signal - do you like to stop gracefully? DO NOT MOVE! MUST BE PLACED AFTER PROCESSES
        signal.signal(signal.SIGINT, self._sigint_handler)

        # stop until someone manually stop us / we receive interrupt signal from os
        # also check if one of the subprocess died
        every_process_is_alright = True
        while every_process_is_alright:
            every_process_is_alright = self.engine.is_alive() and \
                                       self.coach.is_alive() and \
                                       not self.engine.is_any_subprocess_borked()
            if not every_process_is_alright:
                self.logger.critical('One of the engine subprocesses died! Shutting down...')
                self.engine.terminate_subprocesses()
                self.engine.terminate()
                self.coach.terminate()

            # use the time you want here, 0.5 seems sane to me.
            time.sleep(0.5)

    def stop_game(self):
        self.engine.terminate()
        self.coach.terminate()

        exit(0)

    def _sigint_handler(self, *args):
        self.stop_game()

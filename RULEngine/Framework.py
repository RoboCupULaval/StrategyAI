# Under MIT License, see LICENSE.txt
"""
    Point de départ du moteur pour l'intelligence artificielle. Construit les
    objets nécessaires pour maintenir l'état du jeu, acquiert les frames de la
    vision et appelle la stratégie. Ensuite, la stratégie est exécutée et un
    thread est lancé qui contient une boucle qui se charge de l'acquisition des
    frames de la vision. Cette boucle est la boucle principale et appel le
    prochain état du **Coach**.
"""
import logging
from multiprocessing import Process, Event, Queue
import signal  # so we can stop gracefully
import threading  # to stop while runnig the ia and not be obligated to check every loop if we received a stop signal
import time

from RULEngine.engine import Engine
from ai.coach import Coach
from config.config_service import ConfigService


class Framework(object):
    """
        La classe contient la logique nécessaire pour communiquer avec
        les différentes parties(simulation, vision, uidebug et/ou autres),
         maintenir l'état du monde (jeu, referree, debug, etc...) et appeller
         l'ia.
    """

    def __init__(self):
        """ Constructeur de la classe, établis les propriétés de bases et
        construit les objets qui sont toujours necéssaire à son fonctionnement
        correct.
        """

        # logger
        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Framework")
        # config
        self.cfg = ConfigService()

        # Events
        self.ai_terminating_event = Event()
        self.engine_terminating_event = Event()

        # Queues
        self.game_state_queue = Queue()
        self.player_cdms_queue = Queue()
        self.uidebug_queue = Queue()

        # Engine
        self.engine = Engine(self.engine_terminating_event, self.uidebug_queue)
        self.logger.debug("Engine is {0}".format(self.engine))
        self.engine.start()
        self.logger.debug("Engine started {0}".format(self.engine))

        # AI
        self.coach = Coach(self.game_state_queue, self.player_cdms_queue, self.ai_terminating_event)
        self.logger.debug("Coach is {0}".format(self.engine))
        self.coach.start()
        self.logger.debug("Coach started {0}".format(self.engine))

        # endsignal - do you like to stop gracefully? DO NOT MOVE! MUST BE PLACED AFTER PROCESSES
        signal.signal(signal.SIGINT, self._sigint_handler)
        # stop until someone manually stop us / we receive interrupt signal from os
        signal.pause()

    def stop_game(self):
        """
            Nettoie les ressources acquises pour pouvoir terminer l'exécution.
        """
        self.engine_terminating_event.set()
        self.logger.debug("Engine before join = {0}".format(self.engine))
        self.engine.join(1)
        self.logger.debug("Engine after join = {0}".format(self.engine))
        self.ai_terminating_event.set()
        exit(0)

    # noinspection PyUnusedLocal
    def _sigint_handler(self, *args):
        self.stop_game()

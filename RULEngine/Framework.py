# Under MIT License, see LICENSE.txt
"""
    Point de départ du moteur pour l'intelligence artificielle. Construit les
    objets nécessaires pour maintenir l'état du jeu, acquiert les frames de la
    vision et appelle la stratégie. Ensuite, la stratégie est exécutée et un
    thread est lancé qui contient une boucle qui se charge de l'acquisition des
    frames de la vision. Cette boucle est la boucle principale et appel le
    prochain état du **Coach**.
"""
import signal       # so we can stop gracefully
import threading    # to stop while runnig the ia and not be obligated to check every loop if we received a stop signal
import time
import logging
import multiprocessing

from config.config_service import ConfigService
from coach import Coach
from RULEngine.Communication.engine import Engine


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
        # endsignal - do you like to stop gracefully?
        signal.signal(signal.SIGINT, self._sigint_handler)

        # logger
        logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger("Framework")
        # config
        self.cfg = ConfigService()

        # time
        self.last_frame_number = 0
        self.time_stamp = None  # time.time()
        self.last_camera_time = time.time()
        self.time_of_last_loop = time.time()
        self.ai_timestamp = float(self.cfg.config_dict["GAME"]["ai_timestamp"])

        # thread - do not touch without a good reason / see the team before hand

        self.main_thread_terminating_event = threading.Event()
        self.communication_terminating_event = multiprocessing.Event()

        # Communication - do not touch without a good reason / see the team before hand
        self.engine = Engine(self.communication_terminating_event)
        self.logger.debug("Engine is {0}".format(self.engine))
        self.engine.start()
        self.logger.debug("Engine started {0}".format(self.engine))

        self.main_thread = threading.Thread(target=self.game_thread_main_loop, name="AI", daemon=True)
        self.main_thread.start()

        signal.pause()

    def game_thread_main_loop(self):
        """ Fonction exécuté et agissant comme boucle principale. """

        while not self.main_thread_terminating_event.is_set():
            try:
                pass
            except:
                pass

        self.logger.debug("method game_thread_main_loop has exited.")
        exit(0)

    def stop_game(self):
        """
            Nettoie les ressources acquises pour pouvoir terminer l'exécution.
        """
        self.communication_terminating_event.set()
        self.logger.debug("Engine before join = {0}".format(self.engine))
        self.engine.join()
        self.logger.debug("Engine after join = {0}".format(self.engine))
        self.main_thread_terminating_event.set()
        self.logger.debug("Ai before join = {0}".format(self.main_thread))
        self.main_thread.join()
        self.logger.debug("Ai after join = {0}".format(self.main_thread))
        self.logger.debug("Main is alive? {}".format(self.main_thread.is_alive()))
        exit(0)

    # noinspection PyUnusedLocal
    def _sigint_handler(self, *args):
        self.stop_game()

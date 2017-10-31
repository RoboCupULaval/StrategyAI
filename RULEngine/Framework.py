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
import warnings
import logging

from config.config_service import ConfigService
from coach import Coach
from RULEngine.GameDomainObjects.Game import Game
from RULEngine.GameDomainObjects.Referee import Referee
from RULEngine.Util.team_color_service import TeamColorService
from RULEngine.Communication.communication_manager import CommunicationManager


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
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        # config
        self.cfg = ConfigService()

        # time
        self.last_frame_number = 0
        self.time_stamp = None  # time.time()
        self.last_camera_time = time.time()
        self.time_of_last_loop = time.time()
        self.ai_timestamp = float(self.cfg.config_dict["GAME"]["ai_timestamp"])

        # thread - do not touch without a good reason / see the team before hand
        self.main_thread = None
        self.main_thread_terminating_event = threading.Event()
        # Communication
        logging.info("Initializing communication.")
        self.communication_manager = CommunicationManager()
        self.communication_manager.start()
        self.vq = self.communication_manager.vision_queue
        logging.info("Communication initialized.")

        self.start_game()

        self.ai = Coach()
        # # Debug
        # self.incoming_debug = []
        # self.debug = DebugInterface()
        # self.outgoing_debug = self.debug.debug_state

        # # GameDomainObjects elements
        # self.ai_coach = Coach()
        # self.team_color_service = None
        #
        # self._create_game_world()
        #
        # # ia couplage
        # self.ia_coach_mainloop = None
        # self.ia_coach_initializer = None
        #
        # for testing purposes

    def game_thread_main_loop(self):
        """ Fonction exécuté et agissant comme boucle principale. """

        while not self.main_thread_terminating_event.is_set():
            try:
                print(self.vq.pop())
            except:
                pass
            time.sleep(0)
        self.communication_manager.stop()


    def start_game(self):
        """ Démarrage du moteur de l'IA initial, ajustement de l'équipe de l'ia
        et démarrage du/des thread/s"""





        # GAME_WORLD TEAM ADJUSTMENT
        print("Framework partie avec équipe", self.cfg.config_dict["GAME"]["our_color"])
        signal.signal(signal.SIGINT, self._sigint_handler)
        self.main_thread = threading.Thread(target=self.game_thread_main_loop)
        self.main_thread.start()
        time.sleep(65)
        self.stop_game()

    def _create_game_world(self):
        """
            Créé le GameWorld pour contenir les éléments d'une partie normale:
             l'arbitre, la GameDomainObjects (Field, teams, players).
             C'est un data transfer object pour les références du RULEngine vers l'IA
        """

        self.referee = Referee()
        self.game = Game()
        self.game.set_referee(self.referee)

    def _update_players_and_ball(self, vision_frame):
        """ Met à jour le GameState selon la frame de vision obtenue. """
        time_delta = self._compute_vision_time_delta(vision_frame)
        # print(time_delta)
        self.game.update(vision_frame, time_delta)

    def _is_frame_number_different(self, vision_frame):
        # print(vision_frame.detection.frame_number)
        if vision_frame is not None:
            return vision_frame.detection.frame_number != self.last_frame_number
        else:
            return False

    def _compute_vision_time_delta(self, vision_frame):
        self.last_frame_number = vision_frame.detection.frame_number
        this_time = vision_frame.detection.t_capture  # time.time()  # vision_frame.detection.t_capture
        time_delta = this_time - self.last_camera_time
        self.last_camera_time = this_time
        # FIXME: hack
        return time_delta

    def _sim_vision(self):
        vision_frame = self._acquire_last_vision_frame()
        if vision_frame.detection.frame_number != self.last_frame_number:
            time_delta = self._compute_vision_time_delta(vision_frame)
            self.game.update(vision_frame, time_delta)

    def stop_game(self):
        """
            Nettoie les ressources acquises pour pouvoir terminer l'exécution.
        """
        self.main_thread_terminating_event.set()
        self.communication_manager.stop()
        self.communication_manager.join()
        self.main_thread.join()
        # send stop command to all robots
        # stop communication

    # noinspection PyUnusedLocal
    def _sigint_handler(self, *args):
        self.stop_game()

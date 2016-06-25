# Under MIT License, see LICENSE.txt
"""
    Point de départ du moteur pour l'intelligence artificielle. Construit les
    objets nécessaires pour maintenir l'état du jeu, acquiert les frames de la
    vision et construit la stratégie. Ensuite, la stratégie est exécutée et un
    thread est lancé qui contient une boucle qui se charge de l'acquisition des
    frames de la vision. Cette boucle est la boucle principale et appel le
    prochain état du **Coach**.
"""
from collections import deque, namedtuple
import threading
import time

from .Game.Game import Game
from .Game.Referee import Referee
from .Communication.vision import Vision
from .Communication import debug
from .Communication.referee import RefereeServer
from .Communication.udp_server import GrSimCommandSender, DebugCommandSender,\
                                      DebugCommandReceiver
from .Communication.serial_command_sender import SerialCommandSender
from .Command.Command import Stop
from .Util.exception import StopPlayerError

GameState = namedtuple('GameState', ['field', 'referee', 'friends',
                                     'enemies', 'debug'])

class Framework(object):
    """
        La classe contient la logique nécessaire pour démarrer une logique et
        mettre en place l'état du jeu.
    """

    def __init__(self, is_team_yellow=False):
        """ Constructeur de la classe, établis les propriétés de bases. """
        # TODO: refactor pour avoir des objets qui contiennent les petits
        # détails d'implémentations (12/7 fields)
        self.command_sender = None
        self.debug_sender = None
        self.game = None
        self.is_team_yellow = is_team_yellow
        self.strategy = None
        self.referee = None
        self.running_thread = False
        self.last_frame = 0
        self.thread_terminate = threading.Event()
        self.last_time = 0
        self.vision = None


    def create_game(self, strategy):
        """
            Créé l'arbitre et établit la stratégie de l'équipe que l'ia gère.

            :param strategy: Une référence vers une stratégie non instanciée.
            :return: Game, le **GameState**
        """

        self.referee = Referee()

        self.strategy = strategy()

        self.game = Game(self.referee, self.is_team_yellow)

        return self.game


    def update_game_state(self):
        """ Met à jour le **GameState** selon la vision et l'arbitre. """
        # TODO: implémenter correctement la méthode
        pass
        #referee_command = self.referee.get_latest_frame()
        #if referee_command:
        #    pass
            #self.game.update_game_state(referee_command)

    def update_players_and_ball(self):
        """ Met à jour le GameState selon la frame de vision obtenue. """
        vision_frame = self.vision.get_latest_frame()
        if vision_frame and vision_frame.detection.frame_number != self.last_frame:
            self.last_frame = vision_frame.detection.frame_number
            this_time = vision_frame.detection.t_capture
            time_delta = this_time - self.last_time
            self.last_time = this_time
            print("frame: %i, time: %d, delta: %d, FPS: %d" % \
                    (vision_frame.detection.frame_number, this_time, time_delta, 1/time_delta))
            self.game.update(vision_frame, time_delta)

    def update_strategies(self):
        """ Change l'état du **Coach** """

        game_state = self.get_game_state()

        state = self.referee.command.name
        if state == "HALT":
            self.strategy.on_halt(game_state)

        elif state == "NORMAL_START":
            self.strategy.on_start(game_state)

        elif state == "STOP":
            self.strategy.on_stop(game_state)

    def get_game_state(self):
        """ Retourne le **GameState** actuel. *** """

        game = self.game
        return GameState(field=game.field,
                         referee=game.referee,
                         friends=game.friends,
                         enemies=game.enemies,
                         debug={})

    def start_game(self, strategy, async=False, serial=False):
        """ Démarrage du moteur de l'IA initial. """


        # on peut eventuellement demarrer une autre instance du moteur
        if not self.running_thread:
            if serial:
                self.command_sender = SerialCommandSender()
            else:
                self.command_sender = GrSimCommandSender("127.0.0.1", 20011)
            self.debug_sender = DebugCommandSender("127.0.0.1", 20021)
            self.debug_receiver = DebugCommandReceiver("127.0.0.1", 10021)
            self.referee = RefereeServer()
            self.vision = Vision()
        else:
            self.stop_game()

        self.create_game(strategy)

        self.running_thread = threading.Thread(target=self.game_thread)
        self.running_thread.start()

        if not async:
            self.running_thread.join()

    def game_thread(self):
        """ Fonction exécuté et agissant comme boucle principale. """

        times = deque(maxlen=10)
        last_time = time.time()

        # Wait for first frame
        while not self.vision.get_latest_frame():
            time.sleep(0.01)
            print("En attente d'une image de la vision.")

        # TODO: Faire arrêter quand l'arbitre signal la fin de la partie
        while not self.thread_terminate.is_set():
            self.update_game_state()
            self.update_players_and_ball()
            self.update_strategies()
            self._send_robot_commands()

            # s'il n'y a pas de façade, le débogage n'est pas actif
            if self._info_manager().debug_manager:
                self._send_debug_commands()
                self._receive_debug_commands()

            new_time = time.time()
            times.append(new_time - last_time)
            print(len(times) / sum(times))
            last_time = new_time

    def stop_game(self):
        """
            Nettoie les ressources acquises pour pouvoir terminer l'exécution.
        """

        self.thread_terminate.set()
        self.running_thread.join()
        self.thread_terminate.clear()
        try:
            if self.is_team_yellow:
                team = self.game.yellow_team
            else:
                team = self.game.blue_team
            for player in team.players:
                command = Stop(player)
                self.command_sender.send_command(command)
        except:
            print("Could not stop players")
            raise StopPlayerError("Au nettoyage il a été impossible d'arrêter\
                                    les joueurs.")

    def _send_robot_commands(self):
        if self.vision.get_latest_frame(): # pourquoi?
            commands = self._get_coach_commands()
            for command in commands:
                command = command.toSpeedCommand()
                self.command_sender.send_command(command)

    def _get_coach_commands(self):
        return self.strategy.commands


    def _info_manager(self):
        """ Retourne la référence vers l'InfoManager de l'IA. """
        return self.strategy.info_manager

    def _send_debug_commands(self):
        """ Récupère les paquets de débogages et les envoies au serveur. """
        debug_manager = self._info_manager().debug_manager
        if debug_manager:
            debugs_commands = debug.pack_commands(debug_manager)
            self.debug_sender.send_command(debugs_commands)

    def _receive_debug_commands(self):
        """
            Effectue la réception des commandes de débogages du serveur et les
            enregistres dans la façade de débogage.
        """
        commands = debug.unpack_commands(self.debug_receiver.receive_command())
        debug_manager = self._info_manager().debug_manager
        for command in commands:
            type_ = command['type']
            if type_ == 5000:
                debug_manager.toggle_human_control()
            elif type_ == 5001:
                debug_manager.set_strategy(command.data['strategy'])
            elif type_ == 5002:
                debug_manager.set_tactic(command.link, command.data)

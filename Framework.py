# Under MIT License, see LICENSE.txt
"""
    Point de départ du moteur pour l'intelligence artificielle. Construit les
    objets nécessaires pour maintenir l'état du jeu, acquiert les frames de la
    vision et appelle la stratégie. Ensuite, la stratégie est exécutée et un
    thread est lancé qui contient une boucle qui se charge de l'acquisition des
    frames de la vision. Cette boucle est la boucle principale et appel le
    prochain état du **Coach**.
"""
import signal
import threading
import time

# Communication
from RULEngine.Command.command import Stop, Dribbler
from RULEngine.Communication.receiver.referee_receiver import RefereeReceiver
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.sender.serial_command_sender import SerialType, SERIAL_DISABLED
from RULEngine.Communication.util.robot_command_sender_factory import RobotCommandSenderFactory
from RULEngine.Communication.util.serial_protocol import MCUVersion
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender
from RULEngine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from RULEngine.Communication.sender.uidebug_vision_sender import UIDebugVisionSender
# Debug
from RULEngine.Debug.debug_interface import DebugInterface

# Game objects
from RULEngine.Game.Game import Game
from RULEngine.Game.Referee import Referee
from RULEngine.Util.constant import TeamColor
from RULEngine.Util.exception import StopPlayerError
from RULEngine.Util.team_color_service import TeamColorService
from RULEngine.Util.game_world import GameWorld
from RULEngine.Util.image_transformer import ImageTransformer

# TODO inquire about those constants (move, utility)
LOCAL_UDP_MULTICAST_ADDRESS = "224.5.23.2"
UI_DEBUG_MULTICAST_ADDRESS = "127.0.0.1"
CMD_DELTA_TIME = 0.030


class Framework(object):
    """
        La classe contient la logique nécessaire pour communiquer avec
        les différentes parties(simulation, vision, uidebug et/ou autres),
         maintenir l'état du monde (jeu, referree, debug, etc...) et appeller
         l'ia.
    """

    def __init__(self, serial=False, redirect=False, mcu_version=MCUVersion.STM32F407):
        """ Constructeur de la classe, établis les propriétés de bases et
        construit les objets qui sont toujours necéssaire à son fonctionnement
        correct.
        """
        # time
        self.last_frame_number = 0
        self.time_stamp = time.time()
        self.last_time = 0
        self.last_cmd_time = time.time()

        # thread
        self.ia_running_thread = None
        self.thread_terminate = threading.Event()

        # Communication
        self.robot_command_sender = None
        self.vision = None
        self.referee_command_receiver = None
        self.uidebug_command_sender = None
        self.uidebug_command_receiver = None
        self.uidebug_vision_sender = None
        # because this thing below is a callable!
        self.vision_redirecter = lambda *args:None
        self.vision_routine = self._normal_vision

        # Debug
        self.outgoing_debug = []
        self.debug = DebugInterface()

        self._init_communication(serial=serial, redirect=redirect, mcu_version=mcu_version)

        # Game elements
        self.game_world = None
        self.game = None
        self.ai_coach = None
        self.referee = None
        self.team_color_service = None

        self._create_game_world()

        # VISION
        self.image_transformer = ImageTransformer()

        # ia couplage
        self.ia_coach_mainloop = None
        self.ia_coach_initializer = None

        self.debug.add_log(1, "Framework started in {} s".format(time.time() - self.time_stamp))

    def _init_communication(self, serial=SERIAL_DISABLED, debug=True, redirect=False, mcu_version=MCUVersion.STM32F407):
        # first make sure we are not already running
        if self.ia_running_thread is None:
            # where do we send the robots command (serial for bluetooth and rf)
            self.robot_command_sender = RobotCommandSenderFactory.get_sender(serial, mcu_version=mcu_version)

            # do we use the  UIDebug?
            if debug:
                self.uidebug_command_sender = UIDebugCommandSender(UI_DEBUG_MULTICAST_ADDRESS, 20021)
                self.uidebug_command_receiver = UIDebugCommandReceiver(UI_DEBUG_MULTICAST_ADDRESS, 10021)
                # are we redirecting the vision to the uidebug! Work in progress
                if redirect:
                    # TODO merge cameraWork in this to make this work!
                    self.uidebug_vision_sender = UIDebugVisionSender(UI_DEBUG_MULTICAST_ADDRESS, 10022)
                    print(self.uidebug_vision_sender)
                    self.vision_redirecter = self.uidebug_vision_sender.send_packet
                    print(self.vision_redirecter)
                    self.vision_routine = self._redirected_vision
                    print(self.vision_routine)

            self.referee_command_receiver = RefereeReceiver(LOCAL_UDP_MULTICAST_ADDRESS)
            self.vision = VisionReceiver(LOCAL_UDP_MULTICAST_ADDRESS)
        else:
            self.stop_game()

    def game_thread_main_loop(self):
        """ Fonction exécuté et agissant comme boucle principale. """

        self._wait_for_first_frame()

        # TODO: Faire arrêter quand l'arbitre signal la fin de la partie
        while not self.thread_terminate.is_set():
            self.time_stamp = time.time()
            self.vision_routine()

    def start_game(self, p_ia_coach_mainloop, p_ia_coach_initializer,
                   team_color=TeamColor.BLUE_TEAM, async=False):
        """ Démarrage du moteur de l'IA initial, ajustement de l'équipe de l'ia
        et démarrage du/des thread/s"""

        # IA COUPLING
        self.ia_coach_mainloop = p_ia_coach_mainloop
        self.ia_coach_initializer = p_ia_coach_initializer

        # GAME_WORLD TEAM ADJUSTMENT
        self.game_world.game.set_our_team_color(team_color)
        self.team_color_service = TeamColorService(team_color)
        self.game_world.team_color_svc = self.team_color_service
        print("Framework partie avec ", str(team_color))

        self.ia_coach_initializer(self.game_world)

        # THREAD STARTING POINT
        # TODO A quoi sert cette prochaine ligne, elle à l'air mal utilisé
        # s.v.p. reviser
        signal.signal(signal.SIGINT, self._sigint_handler)
        self.ia_running_thread = threading.Thread(target=self.game_thread_main_loop)
        self.ia_running_thread.start()
        if not async:
            self.ia_running_thread.join()

    def _create_game_world(self):
        """
            Créé le GameWorld pour contenir les éléments d'une partie normale:
             l'arbitre, la Game (Field, teams, players).
             C'est un data transfer object pour les références du RULEngine vers l'IA
        """

        self.referee = Referee()
        self.game = Game()
        self.game.set_referee(self.referee)
        self.game_world = GameWorld(self.game)
        self.game_world.set_timestamp(self.time_stamp)

    def _update_players_and_ball(self, vision_frame):
        """ Met à jour le GameState selon la frame de vision obtenue. """
        time_delta = self._compute_vision_time_delta(vision_frame)
        self.game.update(vision_frame, time_delta)

    def _is_frame_number_different(self, vision_frame):
        if vision_frame is not None:
            return vision_frame.detection.frame_number != self.last_frame_number
        else:
            return False

    def _compute_vision_time_delta(self, vision_frame):
        self.last_frame_number = vision_frame.detection.frame_number
        this_time = vision_frame.detection.t_capture
        time_delta = this_time - self.last_time
        self.last_time = this_time
        # FIXME: hack
        return time_delta

    def _update_debug_info(self):
        """ Retourne le **GameState** actuel. *** """

        self.game_world.debug_info += self.uidebug_command_receiver.receive_command()

    def _normal_vision(self):
        vision_frame = self._acquire_last_vision_frame()
        if self._is_frame_number_different(vision_frame):
            self._update_players_and_ball(vision_frame)
            self._update_debug_info()
            robot_commands = self.ia_coach_mainloop()

            # Communication
            self._send_robot_commands(robot_commands)
            self._send_debug_commands()

    def _redirected_vision(self):
        vision_frames = self.vision.pop_frames()
        new_image_packet = self.image_transformer.update(vision_frames)
        self.vision_redirecter(new_image_packet.SerializeToString())

        if self.image_transformer.has_new_image():
            self._update_players_and_ball(new_image_packet)
            self._update_debug_info()
            robot_commands = self.ia_coach_mainloop()

            # Communication
            self._send_robot_commands(robot_commands)
            self._send_debug_commands()

    def _acquire_last_vision_frame(self):
        return self.vision.get_latest_frame()

    def _acquire_all_vision_frames(self):
        return self.vision.pop_frames()

    def stop_game(self):
        """
            Nettoie les ressources acquises pour pouvoir terminer l'exécution.
        """
        self.thread_terminate.set()
        self.ia_running_thread.join()
        self.thread_terminate.clear()
        try:
            team = self.game.friends

            # FIXME: hack real life
            cmd = Dribbler(team.players[4], 0)
            self.robot_command_sender.send_command(cmd)
            for player in team.players.values():
                command = Stop(player)
                #self.robot_command_sender.send_command(command)
        except:
            print("Could not stop players")
            raise StopPlayerError("Au nettoyage il a été impossible d'arrêter les joueurs.")

    def _wait_for_first_frame(self):
        while not self.vision.get_latest_frame():
            time.sleep(0.01)
            print("En attente d'une image de la vision.")

    def _send_robot_commands(self, commands):
        """ Envoi les commades des robots au serveur. """
        time.sleep(CMD_DELTA_TIME)
        for idx, command in enumerate(commands):
            if not isinstance(command, Stop):
                self.robot_command_sender.send_command(command)

    def _send_debug_commands(self):
        """ Envoie les commandes de debug au serveur. """
        self.outgoing_debug = self.debug.debug_state
        packet_represented_commands = [c.get_packet_repr() for c in self.outgoing_debug]
        if self.uidebug_command_sender is not None:
            self.uidebug_command_sender.send_command(packet_represented_commands)

        self.outgoing_debug.clear()

    def _sigint_handler(self, signum, frame):
        self.stop_game()

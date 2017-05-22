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

from RULEngine.Command.command import Stop, Dribbler
from RULEngine.Communication.protobuf import \
    messages_robocup_ssl_wrapper_pb2 as ssl_wrapper
from RULEngine.Communication.receiver.referee_receiver import RefereeReceiver
from RULEngine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender
from RULEngine.Communication.sender.uidebug_vision_sender import UIDebugVisionSender
from RULEngine.Communication.util.robot_command_sender_factory import RobotCommandSenderFactory
from RULEngine.Debug.debug_interface import DebugInterface
from RULEngine.Game.Game import Game
from RULEngine.Game.Referee import Referee
from RULEngine.Util.constant import TeamColor
from RULEngine.Util.game_world import GameWorld
from RULEngine.Util.image_transformer.image_transformer_factory import ImageTransformerFactory
from RULEngine.Util.team_color_service import TeamColorService
from config.config_service import ConfigService


# TODO inquire about those constants (move, utility)


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
        # config
        self.cfg = ConfigService()

        # time
        self.last_frame_number = 0
        self.time_stamp = time.time()
        self.last_time = time.time()
        self.last_cmd_time = time.time()
        self.last_loop = time.time()

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
        # because this thing below is a callable! can be used without being set
        self.vision_redirection_routine = lambda *args: None
        self.vision_routine = self._normal_vision  # self._normal_vision # self._test_vision self._redirected_vision
        self._choose_vision_routines()

        # Debug
        self.incoming_debug = []
        self.outgoing_debug = []
        self.debug = DebugInterface()
        self._init_communication()

        # Game elements
        self.game_world = None
        self.game = None
        self.ai_coach = None
        self.referee = None
        self.team_color_service = None

        self._create_game_world()

        # VISION
        self.image_transformer = ImageTransformerFactory.get_image_transformer()

        # ia couplage
        self.ia_coach_mainloop = None
        self.ia_coach_initializer = None

        # for testing purposes
        self.frame_number = 0

        self.debug.add_log(1, "Framework started in {} s".format(time.time() - self.time_stamp))

    def _choose_vision_routines(self):
        if self.cfg.config_dict["IMAGE"]["kalman"] == "true":
            self.vision_routine = self._kalman_vision
        else:
            self.vision_routine = self._redirected_vision

    def _init_communication(self):
        # first make sure we are not already running
        if self.ia_running_thread is None:
            # where do we send the robots command (serial for bluetooth and rf)
            self.robot_command_sender = RobotCommandSenderFactory.get_sender()
            # Referee
            self.referee_command_receiver = RefereeReceiver()
            # Vision
            self.vision = VisionReceiver()

            # do we use the UIDebug?
            if self.cfg.config_dict["DEBUG"]["using_debug"] == "true":
                self.uidebug_command_sender = UIDebugCommandSender()
                self.uidebug_command_receiver = UIDebugCommandReceiver()
                # are we redirecting the vision to the uidebug!
                if self.cfg.config_dict["COMMUNICATION"]["redirect"] == "true":
                    self.uidebug_vision_sender = UIDebugVisionSender()
                    self.vision_redirection_routine = self.uidebug_vision_sender.send_packet

        else:
            self.stop_game()

    def game_thread_main_loop(self):
        """ Fonction exécuté et agissant comme boucle principale. """

        self._wait_for_first_frame()
        print(self.vision_routine)
        # TODO: Faire arrêter quand l'arbitre signal la fin de la partie
        while not self.thread_terminate.is_set():
            self.time_stamp = time.time()
            self.vision_routine()

    def start_game(self, p_ia_coach_mainloop, p_ia_coach_initializer):
        """ Démarrage du moteur de l'IA initial, ajustement de l'équipe de l'ia
        et démarrage du/des thread/s"""

        # IA COUPLING
        self.ia_coach_mainloop = p_ia_coach_mainloop
        self.ia_coach_initializer = p_ia_coach_initializer

        team_color = self.get_team_color(self.cfg.config_dict["GAME"]["our_color"])
        # GAME_WORLD TEAM ADJUSTMENT
        self.team_color_service = TeamColorService(team_color)
        self.game_world.team_color_svc = self.team_color_service
        print("Framework partie avec ", str(team_color))

        self.ia_coach_initializer(self.game_world)

        signal.signal(signal.SIGINT, self._sigint_handler)
        self.ia_running_thread = threading.Thread(target=self.game_thread_main_loop)
        self.ia_running_thread.start()
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
        self.game_world.set_debug(self.incoming_debug)

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
        time_delta = this_time - self.last_time
        self.last_time = this_time
        # FIXME: hack
        return time_delta

    def _update_debug_info(self):
        self.incoming_debug += self.uidebug_command_receiver.receive_command()

    def _normal_vision(self):
        vision_frame = self._acquire_last_vision_frame()
        if vision_frame.detection.frame_number != self.last_frame_number:
            self._update_players_and_ball(vision_frame)
            self._update_debug_info()
            robot_commands = self.ia_coach_mainloop()
            # Communication

            self._send_robot_commands(robot_commands)
            self.game.set_command(robot_commands)
            self._send_debug_commands()
        time.sleep(0)

    def _test_vision(self):
        vision_frame = self._acquire_last_vision_frame()
        if vision_frame.detection.frame_number != self.last_frame_number:
            self.last_frame_number = vision_frame.detection.frame_number
            this_time = vision_frame.detection.t_capture  # time.time()  # vision_frame.detection.t_capture
            time_delta = this_time - self.last_time
            self.last_time = this_time
            self.game.update(vision_frame, time_delta)
            self._update_debug_info()
            robot_commands = self.ia_coach_mainloop()
            # Communication

            self._send_robot_commands(robot_commands)
            self.game.set_command(robot_commands)
            self._send_debug_commands()
        time.sleep(0)

    def _kalman_vision(self):
        vision_frames = self.vision.pop_frames()
        new_image_packet = self.image_transformer.update(vision_frames)
        self.game.field.update_field_dimensions(vision_frames)

        if time.time() - self.last_loop > 0.05:
            time_delta = time.time() - self.last_time
            self.game.update_kalman(new_image_packet, time_delta)
            self._update_debug_info()
            robot_commands = self.ia_coach_mainloop()
            # Communication

            self._send_robot_commands(robot_commands)
            self.game.set_command(robot_commands)
            self._send_debug_commands()
            self._send_new_vision_packet()
            self.last_time = time.time()
            self.last_loop = time.time()
        time.sleep(0)

    def _redirected_vision(self):
        vision_frames = self.vision.pop_frames()
        new_image_packet = self.image_transformer.update(vision_frames)

        if time.time() - self.last_loop > 0.05:
            self.vision_redirection_routine(new_image_packet.SerializeToString())
            time_delta = time.time() - self.last_time
            self.game.update(new_image_packet, time_delta)
            self.last_time = time.time()
            self.last_frame_number = new_image_packet.detection.frame_number
            self._update_debug_info()
            robot_commands = self.ia_coach_mainloop()

            # Communication
            self._send_robot_commands(robot_commands)
            self.game.set_command(robot_commands)
            self._send_debug_commands()
            self.last_loop = time.time()
        else:
            time.sleep(0)

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
        self.robot_command_sender.stop()
        try:
            team = self.game.friends

            # FIXME: hack real life
            cmd = Dribbler(team.players[4], 0)
            self.robot_command_sender.send_command(cmd)
            for player in team.players.values():
                command = Stop(player)
                self.robot_command_sender.send_command(command)
        except:
            print("Could not stop players")
            print("Au nettoyage il a été impossible d'arrêter les joueurs.")
            # raise StopPlayerError("Au nettoyage il a été impossible d'arrêter les joueurs.")

    def _wait_for_first_frame(self):
        while not self.vision.get_latest_frame() and not self.thread_terminate.is_set():
            time.sleep(0.01)
            print("En attente d'une image de la vision.")

    def _send_robot_commands(self, commands):
        """ Envoi les commades des robots au serveur. """
        for command in commands:
            self.robot_command_sender.send_command(command)

    def _send_debug_commands(self):
        """ Envoie les commandes de debug au serveur. """
        self.outgoing_debug = self.debug.debug_state
        packet_represented_commands = [c.get_packet_repr() for c in self.outgoing_debug]
        if self.uidebug_command_sender is not None:
            self.uidebug_command_sender.send_command(packet_represented_commands)

        self.incoming_debug.clear()
        self.outgoing_debug.clear()

    # for testing purposes
    def _send_new_vision_packet(self):
        pb_sslwrapper = ssl_wrapper.SSL_WrapperPacket()
        pb_sslwrapper.detection.camera_id = 0
        pb_sslwrapper.detection.t_sent = 0

        pck_ball = pb_sslwrapper.detection.balls.add()
        pck_ball.x = self.game.field.ball.position.x
        pck_ball.y = self.game.field.ball.position.y
        pck_ball.z = self.game.field.ball.position.z
        # required for the packet no use for us at this stage
        pck_ball.confidence = 0.999
        pck_ball.pixel_x = self.game.field.ball.position.x
        pck_ball.pixel_y = self.game.field.ball.position.y

        for p in self.game.blue_team.players.values():
            packet_robot = pb_sslwrapper.detection.robots_blue.add()
            packet_robot.confidence = 0.999
            packet_robot.robot_id = p.id
            packet_robot.x = p.pose.position.x
            packet_robot.y = p.pose.position.y
            packet_robot.orientation = p.pose.orientation
            packet_robot.pixel_x = 0.
            packet_robot.pixel_y = 0.

        for p in self.game.yellow_team.players.values():
            packet_robot = pb_sslwrapper.detection.robots_yellow.add()
            packet_robot.confidence = 0.999
            packet_robot.robot_id = p.id
            packet_robot.x = p.pose.position.x
            packet_robot.y = p.pose.position.y
            packet_robot.orientation = p.pose.orientation
            packet_robot.pixel_x = 0.
            packet_robot.pixel_y = 0.

        self.frame_number += 1
        pb_sslwrapper.detection.t_capture = 0
        pb_sslwrapper.detection.frame_number = self.frame_number

        self.vision_redirection_routine(pb_sslwrapper.SerializeToString())

    def _sigint_handler(self, *args):
        self.stop_game()

    @staticmethod
    def get_team_color(teamcolor: str):
        if teamcolor == "blue":
            return TeamColor.BLUE_TEAM
        if teamcolor == "yellow":
            return TeamColor.YELLOW_TEAM

# Under MIT License, see LICENSE.txt

import logging
import os
import sys
from multiprocessing import Process, Queue
from queue import Full
from time import time

from RULEngine.Communication.receiver.uidebug_command_receiver import UIDebugCommandReceiver
from RULEngine.Communication.receiver.vision_receiver import VisionReceiver
from RULEngine.Communication.receiver.referee_receiver import RefereeReceiver

from RULEngine.Communication.sender.robot_command_sender import RobotCommandSender
from RULEngine.Communication.sender.uidebug_command_sender import UIDebugCommandSender

from RULEngine.Debug.uidebug_command_factory import UIDebugCommandFactory

from RULEngine.controller import Controller
from RULEngine.tracker import Tracker

try:
    from Util.csv_plotter import CsvPlotter
except:
    print("Fail to import csv_plotter. It will be disable.")
    from RULEngine.controller import Observer as CsvPlotter

from config.config_service import ConfigService

__author__ = "Maxime Gagnon-Legault and Simon Bouchard"


class Engine(Process):
    VISION_QUEUE_MAXSIZE = 1
    ROBOT_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_SENDER_QUEUE_MAXSIZE = 100
    UI_DEBUG_COMMAND_RECEIVER_QUEUE_MAXSIZE = 100
    REFEREE_QUEUE_MAXSIZE = 100
    # FPS = 30

    def __init__(self, game_state_queue: Queue,
                 ai_queue: Queue,
                 referee_queue: Queue,
                 ui_send_queue: Queue,
                 ui_recv_queue: Queue):
        super(Engine, self).__init__(name=__name__)

        self.logger = logging.getLogger('Engine')
        self.cfg = ConfigService()
        self.team_color = self.cfg.config_dict['GAME']['our_color']

        self.vision_queue = Queue(maxsize=Engine.VISION_QUEUE_MAXSIZE)
        self.ui_send_queue = ui_send_queue
        self.ui_recv_queue = ui_recv_queue
        self.ai_queue = ai_queue
        self.referee_queue = referee_queue
        self.game_state_queue = game_state_queue
        self.robot_cmd_queue = Queue()

        # vision subprocess
        vision_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'],
                                  int(self.cfg.config_dict['COMMUNICATION']['vision_port']))

        self.vision_receiver = VisionReceiver(vision_connection_info, self.vision_queue)

        # UIDebug communication subprocesses
        ui_debug_host = self.cfg.config_dict['COMMUNICATION']['ui_debug_address']
        ui_sender_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_sender_port']))
        ui_recver_connection_info = (ui_debug_host, int(self.cfg.config_dict['COMMUNICATION']['ui_cmd_receiver_port']))

        self.ui_sender = UIDebugCommandSender(ui_sender_connection_info, self.ui_send_queue)
        self.ui_recver = UIDebugCommandReceiver(ui_recver_connection_info, self.ui_recv_queue)

        # Referee communication
        referee_recver_connection_info = (self.cfg.config_dict['COMMUNICATION']['referee_udp_address'],
                                           int(self.cfg.config_dict['COMMUNICATION']['referee_port']))
        self.referee_recver = RefereeReceiver(referee_recver_connection_info, self.referee_queue)

        # Subprocess to send robot commands
        robot_connection_info = (self.cfg.config_dict['COMMUNICATION']['vision_udp_address'], 20011)

        self.robot_cmd_sender = RobotCommandSender(robot_connection_info, self.robot_cmd_queue)

        self.tracker = Tracker(self.vision_queue)
        self.controller = Controller(self.ai_queue, CsvPlotter)

        # print framerate
        self.framecount = 0
        self.time_last_print = time()

    def start(self):
        super().start()
        self.vision_receiver.start()
        self.ui_sender.start()
        self.ui_recver.start()
        self.referee_recver.start()
        self.robot_cmd_sender.start()

    def run(self):
        own_pid = os.getpid()
        self.logger.debug('Running with process ID {}'.format(own_pid))

        try:
            while True:

                # start = time()

                track_frame = self.tracker.update()
                robot_packets_frame = self.controller.execute(track_frame)

                self.robot_cmd_queue.put(robot_packets_frame)

                self.tracker.predict(robot_packets_frame.packet)

                try:
                    self.game_state_queue.put(track_frame, block=False)
                except Full:
                    pass

                self.ui_send_queue.put(UIDebugCommandFactory.track_frame(track_frame))
                self.ui_send_queue.put(UIDebugCommandFactory.robots_path(self.controller))

                # sleep_time = max(1/Engine.FPS - (time() - start), 0)
                # if sleep_time > 0:
                #     sleep(sleep_time)
                # else:
                #     self.logger.debug('main loop take too much time.')

                self.print_framerate()

        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info('Killed')

        sys.stdout.flush()
        exit(0)

    def is_any_subprocess_borked(self):
        borked_process_found = not self.vision_receiver.is_alive() or \
                               not self.ui_sender.is_alive() or \
                               not self.ui_recver.is_alive() or \
                               not self.robot_cmd_sender.is_alive()
        return borked_process_found

    def terminate_subprocesses(self):
        self.vision_receiver.terminate()
        self.ui_sender.terminate()
        self.ui_recver.terminate()
        self.robot_cmd_sender.terminate()

    def print_framerate(self):
        self.framecount += 1
        dt = time() - self.time_last_print
        if dt > 2:
            self.logger.info('Updating at {:.2f} fps'.format(self.framecount / dt))
            self.time_last_print = time()
            self.framecount = 0
